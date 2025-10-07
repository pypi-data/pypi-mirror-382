# model.py
# -*- coding: utf-8 -*-
"""
LarkModel: 字节级文本编码 + 边界预测 + 分段解码模型
"""

import math
import torch
from torch import nn, Tensor
from torch.distributions.gumbel import Gumbel


# ---------------------- 模型配置 ----------------------
START_BYTE = 256
END_BYTE = 257
PAD_BYTE = 258
VOCAB_SIZE = 259  # 0~255 + START + END + PAD
MAX_LEN = 128  # 最大字节数(示例)








# ---------------------- 编码器 ----------------------
class ByteEncoder(nn.Module):
    """
    将字节序列编码为上下文表示 (B, L, D)
    """

    def __init__(self, d_model=128, n_layers=2, n_heads=4, ff=512,
                 max_len=512, dtype=torch.bfloat16):
        super().__init__()
        self.byte_emb = nn.Embedding(
            VOCAB_SIZE, d_model, padding_idx=PAD_BYTE, dtype=dtype
        )
        self.pos_emb = nn.Parameter(torch.zeros(1, max_len, d_model, dtype=dtype))

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=ff,
            batch_first=True, dtype=dtype
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)

    def forward(self, x_bytes: Tensor, pad_mask: Tensor = None) -> Tensor:
        """
        Args:
            x_bytes: (B, L) 字节id序列
            pad_mask: (B, L) 1=有效，0=PAD
        Returns:
            (B, L, D)
        """
        B, L = x_bytes.shape
        h = self.byte_emb(x_bytes) + self.pos_emb[:, :L, :]

        src_key_padding_mask = (pad_mask == 0) if pad_mask is not None else None
        causal_mask = torch.triu(
            torch.ones(L, L, device=x_bytes.device), diagonal=1
        ).bool()

        return self.encoder(h, mask=causal_mask, src_key_padding_mask=src_key_padding_mask)


# ---------------------- 边界预测器 ----------------------
def gumbel_sigmoid(logits: Tensor, temp: float = 1.0, hard: bool = False,
                   threshold: float = 0.5) -> Tensor:
    """
    Gumbel-Sigmoid 采样，用于离散边界预测
    """
    if not (0 < temp < 1):
        raise ValueError("Temperature must be in (0, 1)")

    g = Gumbel(0, 1).sample((2, *logits.shape)).to(logits.device)
    out = torch.sigmoid((logits + g[0] - g[1]) / temp)

    if hard:
        indices = out > threshold
        out = indices.int() - out.detach() + out
    return out


class BatchBoundaryPredictor(nn.Module):
    """
    预测序列中的 segment 边界
    """

    def __init__(self, d_model, init_tau=0.4, min_tau=0.0001, anneal_rate=1e-4, dtype=torch.bfloat16):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(d_model, d_model // 2, dtype=dtype),
            nn.GELU(),
            nn.Linear(d_model // 2, 1, dtype=dtype),
        )
        self.register_buffer("tau", torch.tensor(init_tau))
        self.min_tau = min_tau
        self.anneal_rate = anneal_rate
        self.train_step = 0

    def _update_tau(self):
        """指数退火 tau"""
        self.train_step += 1
        new_tau = max(
            self.min_tau,
            float(self.tau * math.exp(-self.anneal_rate * self.train_step))
        )
        self.tau = torch.tensor(new_tau, device=self.tau.device)

    def forward(
        self,
        x: Tensor,
        pad_mask: Tensor = None,
        boundary_force_mask: Tensor = None
    ) -> Tensor:
        """
        根据输入的序列 x 和 pad_mask，预测其中的 segment 边界。

        Args:
            x: 输入序列，形状为 [B, T, D]
            pad_mask: 填充掩码，形状为 [B, T]
            boundary_force_mask: 强制边界掩码，形状为 [B, T], 1 则强制为边界，0 则正常预测

        Returns:
            预测的边界，形状为 [B, T]
        """
        logits = self.mlp(x)
        # 修改这里：避免使用 view 中的动态形状计算
        batch_size, seq_len, _ = x.shape
        logits = logits.reshape(batch_size, seq_len).to(torch.float32)  # 使用 reshape 替代 view
        y = logits
        if self.training:
            self._update_tau()
            y = gumbel_sigmoid(logits, temp=float(self.tau), hard=True)
        else:
            y = (torch.sigmoid(logits) > 0.5).float()

        if pad_mask is not None:
            y = y * pad_mask.float()

        # 应用强制边界掩码，对onnx不友好
        if boundary_force_mask is not None:
            y = torch.where(boundary_force_mask > 0, torch.ones_like(y), y)
        #强制 CLS 首 token 为边界
        y[:, 0] = 1
        
        return y.to(torch.long)


# ---------------------- Downsample ----------------------
def downsample_batch(hidden: Tensor, hard_boundary: Tensor,
                     encoder: ByteEncoder):
    """
    按边界选择 hidden，形成 segment embeddings
    """
    B, T, H = hidden.shape
    device = hidden.device
    pad_emb = encoder.byte_emb(torch.tensor([PAD_BYTE], device=device))  # [1,H]

    flat_hidden = hidden.reshape(-1, H)
    flat_boundary = hard_boundary.reshape(-1)
    idx = torch.nonzero(flat_boundary, as_tuple=False).squeeze(-1)
    selected_tokens = flat_hidden[idx]

    seg_counts = hard_boundary.sum(dim=1)
    max_len = int(seg_counts.max().item())

    padded_segments = pad_emb.expand(B, max_len, H).clone()
    masks = torch.zeros(B, max_len, device=device)

    start = 0
    for b in range(B):
        n = int(seg_counts[b].item())
        if n > 0:
            padded_segments[b, :n] = selected_tokens[start:start+n]
            masks[b, :n] = 1
            start += n

    return padded_segments, masks


# ---------------------- 解码器 ----------------------
class Decoder(nn.Module):
    """
    基于 Transformer 的 segment 级解码器
    """

    def __init__(self, d_model, n_heads, n_layers, ff, label_size,
                 max_len=MAX_LEN, dropout=0.1, dtype=torch.bfloat16):
        super().__init__()
        self.transformer_layers = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=d_model, nhead=n_heads, dim_feedforward=ff,
                dropout=dropout, batch_first=True, dtype=dtype
            )
            for _ in range(n_layers)
        ])
        self.lm_head = nn.Linear(d_model, label_size, dtype=dtype)
        self.pos_emb = nn.Parameter(torch.zeros(1, max_len, d_model, dtype=dtype))
        self.cls_segment_embedding = nn.Parameter(torch.zeros(1, 1, d_model, dtype=dtype))

    def forward(self, segment_embeddings: Tensor, segment_mask: Tensor) -> Tensor:
        B, L, H = segment_embeddings.shape
        x = segment_embeddings + self.pos_emb[:, :L, :]
        x = self.cls_segment_embedding.expand(B, 1, H) + x

        for layer in self.transformer_layers:
            x = layer(x, src_key_padding_mask=~segment_mask.bool())

        cls_embedding = x[:, 0, :]  # [B, H]
        return self.lm_head(cls_embedding)


# ---------------------- 总模型 ----------------------
class LarkModel(nn.Module):
    """
    LarkModel: 字节编码 + 边界预测 + segment 解码
    """

    def __init__(self, d_model=128, n_layers=2, n_heads=4, ff=512,
                 label_size=2, dropout=0.1, max_len=MAX_LEN, dtype=torch.bfloat16):
        super().__init__()
        self.encoder = ByteEncoder(
            d_model=d_model, n_layers=n_layers, n_heads=n_heads,
            ff=ff, max_len=max_len, dtype=dtype
        )
        self.predictor = BatchBoundaryPredictor(d_model=d_model, dtype=dtype)
        self.decoder = Decoder(
            d_model=d_model, n_heads=n_heads, n_layers=n_layers,
            ff=ff, max_len=max_len, label_size=label_size,
            dropout=dropout, dtype=dtype
        )

    def forward(self, x_bytes: Tensor, pad_mask: Tensor = None) -> Tensor:
        h = self.encoder(x_bytes, pad_mask)
        hard_boundary = self.predictor(h, pad_mask)
        segment_embeddings, segment_mask = downsample_batch(h, hard_boundary, self.encoder)
        return self.decoder(segment_embeddings, segment_mask)


# ---------------------- 工具函数 ----------------------
def model_size_in_mb(model: nn.Module, dtype=torch.float32) -> float:
    """
    计算模型存储大小 (MB)
    """
    dtype_to_bytes = {
        torch.float32: 4, torch.float64: 8, torch.float16: 2,
        torch.bfloat16: 2, torch.int32: 4, torch.int64: 8,
        torch.int16: 2, torch.int8: 1, torch.uint8: 1,
    }
    if dtype not in dtype_to_bytes:
        raise ValueError(f"Unsupported dtype {dtype}")
    element_bytes = dtype_to_bytes[dtype]
    param_size = sum(p.numel() * element_bytes for p in model.parameters())
    buffer_size = sum(b.numel() * element_bytes for b in model.buffers())
    return (param_size + buffer_size) / (1024 ** 2)


__all__ = [
    "ByteEncoder", "BatchBoundaryPredictor", "Decoder",
    "LarkModel", "model_size_in_mb"
]


# ---------------------- 测试入口 ----------------------
if __name__ == "__main__":
    x_bytes = torch.randint(0, VOCAB_SIZE, (2, 128))
    pad_mask = torch.randint(0, 2, (2, 128)).bool()

    model = LarkModel(d_model=128, n_layers=2, n_heads=4,
                      ff=512, label_size=233, dropout=0.1)

    logits = model(x_bytes, pad_mask)
    print("logits:", logits.shape)
    print(f"Model size (float16): {model_size_in_mb(model, dtype=torch.float16):.2f} MB")
