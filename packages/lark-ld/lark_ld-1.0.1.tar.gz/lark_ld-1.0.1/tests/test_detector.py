"""
Tests for Lark language detector
"""

import pytest
import torch
from lark import LarkDetector, detect_language


class TestLarkDetector:
    """Test cases for LarkDetector"""
    
    def test_detector_initialization(self):
        """Test that detector initializes correctly"""
        detector = LarkDetector()
        assert detector is not None
        assert hasattr(detector, 'model')
        assert hasattr(detector, 'id2label')
        assert len(detector.id2label) > 0
    
    def test_detect_english(self):
        """Test detection of English text"""
        detector = LarkDetector()
        text = "Hello, how are you doing today?"
        language, confidence = detector.detect(text)
        assert language == "en"
        assert 0 <= confidence <= 1
    
    def test_detect_chinese(self):
        """Test detection of Chinese text"""
        detector = LarkDetector()
        text = "今天的天气真不错，我们一起去公园散步吧！"
        language, confidence = detector.detect(text)
        assert language == "zh"
        assert 0 <= confidence <= 1
    
    def test_detect_japanese(self):
        """Test detection of Japanese text"""
        detector = LarkDetector()
        text = "こんにちは！今日はどんな一日でしたか？"
        language, confidence = detector.detect(text)
        assert language == "ja"
        assert 0 <= confidence <= 1
    
    def test_batch_detection(self):
        """Test batch language detection"""
        detector = LarkDetector()
        texts = [
            "Hello world!",
            "今天天气真好",
            "こんにちは"
        ]
        results = detector.detect_batch(texts)
        
        assert len(results) == len(texts)
        for (language, confidence) in results:
            assert 0 <= confidence <= 1
            assert isinstance(language, str)
    
    def test_topk_predictions(self):
        """Test top-k predictions"""
        detector = LarkDetector()
        text = "This is a sample English text"
        language, confidence, top_k = detector.detect_with_topk(text, k=3)
        
        assert language == "en"
        assert 0 <= confidence <= 1
        assert len(top_k) == 3
        for item in top_k:
            assert 'language' in item
            assert 'probability' in item
            assert 0 <= item['probability'] <= 1
    
    def test_confidence_threshold(self):
        """Test confidence threshold functionality"""
        detector = LarkDetector()
        text = "Short ambiguous text"
        language, confidence, top_k = detector.detect_with_confidence(
            text, confidence_threshold=0.9
        )
        
        # This might return "unknown" if confidence is low
        assert isinstance(language, str)
        assert 0 <= confidence <= 1
        assert len(top_k) > 0
    
    def test_supported_languages(self):
        """Test getting supported languages"""
        detector = LarkDetector()
        languages = detector.get_supported_languages()
        
        assert isinstance(languages, list)
        assert len(languages) > 0
        assert "en" in languages
        assert "zh" in languages
        assert "ja" in languages
    
    def test_convenience_function(self):
        """Test the convenience function"""
        text = "Hello world"
        language, confidence = detect_language(text)
        
        assert language == "en"
        assert 0 <= confidence <= 1


class TestModelComponents:
    """Test individual model components"""
    
    def test_tokenizer(self):
        """Test tokenizer functionality"""
        from lark.tokenizer import batch_tokenize, encode2bytes, decode2text
        
        # Test encode/decode
        text = "Hello"
        encoded = encode2bytes(text)
        decoded = decode2text(encoded)
        assert decoded == text
        
        # Test batch tokenize
        texts = ["Hello", "World"]
        token_ids, pad_mask = batch_tokenize(texts, max_len=10)
        
        assert token_ids.shape[0] == len(texts)
        assert pad_mask.shape[0] == len(texts)
        assert token_ids.shape[1] == 10
        assert pad_mask.shape[1] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
