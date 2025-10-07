START_BYTE = 256
END_BYTE = 257
PAD_BYTE = 258
VOCAB_SIZE = 259  # 0~255 + START + END + PAD

import torch
torch.backends.mha.set_fastpath_enabled(False)

def encode2bytes(text: str) -> list[int]:
    return list(text.encode("utf-8"))

def decode2text(byte_list: list[int]) -> str:
    return bytes([b for b in byte_list if b < 256]).decode("utf-8", errors="ignore")

# ---------------- 批次编码 + pad ----------------
def batch_tokenize(texts: list[str], max_len=128):
    """
    texts: list of str
    # max_len 建议训练时尽量不要进行裁剪操作，这会导致最后一个字节的语义不完整
    返回:
        token_ids: B x L_longest (LongTensor)
        pad_mask: B x L_longest (1 表示 padding, 0 表示有效)
    """
    byte_lists = []
    for text in texts:
        if text == "":
            # 特殊情况，仅在推理时有效，后续可以换成特定字符
            byte_seq =[START_BYTE]
            max_len =1
        else:
            byte_seq =[START_BYTE]+encode2bytes(text)+[END_BYTE]
        byte_lists.append(torch.LongTensor(byte_seq))
    #max_len = max([len(b) for b in byte_lists])
    
    
    # pad sequences
    padded = []
    pad_mask = []
    for b in byte_lists:
        if len(b) >= max_len:
            padded.append(b[:max_len])
            pad_mask.append(torch.ones(max_len))
        else:
            pad_len = max_len - len(b)
            padded.append(torch.cat([b, torch.full((pad_len,), PAD_BYTE, dtype=torch.long)]))
            pad_mask.append(torch.cat([torch.ones(len(b)), torch.zeros(pad_len)]))  #1=有效, 0=padding

    token_ids = torch.stack(padded, dim=0)       # B x L
    pad_mask = torch.stack(pad_mask, dim=0)      # B x L
    return token_ids, pad_mask
