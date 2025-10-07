"""
LarkDetector - Main interface for language detection
"""

import torch
import json
import os
import requests
from typing import List, Tuple, Dict, Optional
from .model import LarkModel
from .tokenizer import batch_tokenize


def download_from_huggingface(url: str, local_path: str, timeout: int = 10) -> bool:
    """
    Download file from HuggingFace with timeout.
    
    Args:
        url: HuggingFace file URL
        local_path: Local path to save the file
        timeout: Download timeout in seconds
        
    Returns:
        True if download successful, False otherwise
    """
    try:
        print(f"📥 Downloading from {url}...")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded successfully: {local_path}")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False


class LarkDetector:
    """
    Main language detection interface for Lark model.
    
    This class provides a simple API for detecting languages in text
    using the byte-level Lark model.
    """
    
    def __init__(self, model_path: Optional[str] = None, labels_path: Optional[str] = None):
        """
        Initialize the language detector.
        
        Args:
            model_path: Path to the model weights file. If None, uses default path.
            labels_path: Path to the labels JSON file. If None, uses default path.
        """
        # Set default paths
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "..", "lark_epoch1.pth")
        if labels_path is None:
            labels_path = os.path.join(os.path.dirname(__file__), "..", "all_dataset_labels.json")
        
        # Download model and labels if they don't exist
        if not os.path.exists(model_path):
            print("🔍 Model file not found locally, downloading from HuggingFace...")
            model_url = "https://hf-mirror.com/jiangchengchengNLP/Lark/resolve/main/lark_epoch1.pth"
            if not download_from_huggingface(model_url, model_path):
                print("⚠️ Using randomly initialized model")
        
        if not os.path.exists(labels_path):
            print("🔍 Labels file not found locally, downloading from HuggingFace...")
            labels_url = "https://hf-mirror.com/jiangchengchengNLP/Lark/resolve/main/all_dataset_labels.json"
            if not download_from_huggingface(labels_url, labels_path):
                raise FileNotFoundError("Labels file not found and download failed")
        
        # Load model
        self.model = LarkModel(
            d_model=256, n_layers=4, n_heads=8, ff=512,
            label_size=102, dropout=0.0, max_len=1024
        )
        
        # Load weights
        try:
            state_dict = torch.load(model_path, map_location='cpu')
            self.model.load_state_dict(state_dict, strict=True)
            print(f"✅ Model weights loaded successfully: {model_path}")
        except Exception as e:
            print(f"⚠️ Weight loading failed: {e}")
            print("Using randomly initialized model")
        
        self.model.eval()
        
        # Load label mapping
        with open(labels_path, "r", encoding="utf-8") as f:
            all_labels = json.load(f)["all_labels"]
        self.id2label = {i: lang for i, lang in enumerate(all_labels)}
        self.label2id = {lang: i for i, lang in enumerate(all_labels)}
        
        print(f"✅ Number of labels: {len(self.id2label)}")
        print(f"✅ Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    def detect(self, text: str, max_len: int = 1024) -> Tuple[str, float]:
        """
        Detect language for a single text.
        
        Args:
            text: Input text string
            max_len: Maximum sequence length
            
        Returns:
            Tuple of (detected_language, confidence_score)
        """
        predictions, probabilities = self._predict_batch([text], max_len)
        confidence = probabilities[0].max().item()
        return predictions[0], confidence
    
    def detect_batch(self, texts: List[str], max_len: int = 1024) -> List[Tuple[str, float]]:
        """
        Batch language detection for multiple texts.
        
        Args:
            texts: List of input text strings
            max_len: Maximum sequence length
            
        Returns:
            List of tuples (detected_language, confidence_score) for each text
        """
        predictions, probabilities = self._predict_batch(texts, max_len)
        results = []
        for pred, prob in zip(predictions, probabilities):
            confidence = prob.max().item()
            results.append((pred, confidence))
        return results
    
    def detect_with_topk(self, text: str, k: int = 5, max_len: int = 1024) -> Tuple[str, float, List[Dict]]:
        """
        Get top-k language predictions with probabilities.
        
        Args:
            text: Input text string
            k: Number of top predictions to return
            max_len: Maximum sequence length
            
        Returns:
            Tuple of (predicted_language, confidence, top_k_predictions)
            where top_k_predictions is a list of dicts with 'language' and 'probability'
        """
        predictions, probabilities = self._predict_batch([text], max_len)
        probs = probabilities[0]
        top_probs, top_indices = torch.topk(probs, k=min(k, len(probs)))
        
        top_k = []
        for prob, idx in zip(top_probs, top_indices):
            top_k.append({
                "language": self.id2label[int(idx.item())],
                "probability": prob.item()
            })
        
        return predictions[0], probabilities[0].max().item(), top_k
    
    def detect_with_confidence(self, text: str, confidence_threshold: float = 0.5, 
                             max_len: int = 1024) -> Tuple[str, float, List[Dict]]:
        """
        Language detection with confidence threshold.
        
        Args:
            text: Input text string
            confidence_threshold: Minimum confidence to return a prediction
            max_len: Maximum sequence length
            
        Returns:
            Tuple of (predicted_language, confidence, top_k_predictions)
            If confidence < threshold, language will be "unknown"
        """
        prediction, confidence, top_k = self.detect_with_topk(text, k=5, max_len=max_len)
        
        if confidence < confidence_threshold:
            return "unknown", confidence, top_k
        else:
            return prediction, confidence, top_k
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of all supported languages.
        
        Returns:
            List of language codes supported by the model
        """
        return list(self.id2label.values())
    
    def _predict_batch(self, texts: List[str], max_len: int = 1024) -> Tuple[List[str], torch.Tensor]:
        """
        Internal batch prediction method.
        
        Args:
            texts: List of input texts
            max_len: Maximum sequence length
            
        Returns:
            Tuple of (predictions, probabilities)
        """
        # Tokenize
        token_ids, pad_mask = batch_tokenize(texts, max_len=max_len)
        
        # Inference
        with torch.no_grad():
            logits = self.model(token_ids, pad_mask)
        
        # Process output
        if logits.dim() == 3:  
            cls_logits = logits[:, 0, :]     # [B, label_size]
        else:
            cls_logits = logits              # [B, label_size]
        
        # Calculate probabilities
        probabilities = torch.softmax(cls_logits, dim=-1)
        
        # Get predictions
        preds = torch.argmax(cls_logits, dim=-1)
        predictions = [self.id2label[int(p.item())] for p in preds]
        
        return predictions, probabilities


# Convenience function for quick usage
def detect_language(text: str, model_path: Optional[str] = None) -> Tuple[str, float]:
    """
    Convenience function for quick language detection.
    
    Args:
        text: Input text string
        model_path: Optional path to model weights
        
    Returns:
        Tuple of (detected_language, confidence_score)
    """
    detector = LarkDetector(model_path=model_path)
    return detector.detect(text)


# Example usage
if __name__ == "__main__":
    # Quick test
    detector = LarkDetector()
    
    test_texts = [
        "Hello, how are you doing today?",
        "今天的天气真不错，我们一起去公园散步吧！",
        "こんにちは！今日はどんな一日でしたか？"
    ]
    
    print("=== Language Detection Test ===")
    for text in test_texts:
        language, confidence = detector.detect(text)
        print(f"'{text[:30]}...' -> {language} (confidence: {confidence:.4f})")
