# Lark - Byte-Level Language Detection

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Lark is a byte-level language detection model that supports **102 languages** with high accuracy and efficiency.

## 🚀 Features

- **102 Languages**: Supports a wide range of languages including English, Chinese, Japanese, Spanish, French, etc.
- **Byte-Level Processing**: No vocabulary limitations, handles any Unicode text
- **High Accuracy**: State-of-the-art performance on language detection tasks
- **Fast Inference**: Optimized for both CPU and GPU
- **Easy Integration**: Simple API for both batch and single text processing

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install lark-ld
```

### From Source
```bash
git clone https://github.com/farshore-byte/LarkDetect.git
cd LarkDetect
pip install -e .
```

## 🎯 Quick Start

### Basic Usage
```python
from lark import LarkDetector

# Initialize detector
detector = LarkDetector()

# Detect language for single text
text = "Hello, how are you today?"
language, confidence = detector.detect(text)
print(f"Language: {language}, Confidence: {confidence:.4f}")

# Batch detection
texts = [
    "Hello world!",
    "今天天气真好",
    "こんにちは、元気ですか？"
]
results = detector.detect_batch(texts)
for text, (lang, conf) in zip(texts, results):
    print(f"'{text}' -> {lang} ({conf:.4f})")
```

### Advanced Usage
```python
from lark import LarkDetector

detector = LarkDetector()

# Get top-k predictions
text = "This is a sample text"
prediction, confidence, top_k = detector.detect_with_topk(text, k=5)
print(f"Prediction: {prediction} (Confidence: {confidence:.4f})")
print("Top 5 predictions:")
for i, item in enumerate(top_k):
    print(f"  {i+1}. {item['language']:8} - {item['probability']:.4f}")

# Confidence threshold
language, confidence, top_k = detector.detect_with_confidence(
    text, 
    confidence_threshold=0.7
)
if language == "unknown":
    print(f"Low confidence: {confidence:.4f}")
else:
    print(f"Detected: {language} (Confidence: {confidence:.4f})")
```

## 📊 Supported Languages

Lark supports 102 languages including:

- **European**: English, Spanish, French, German, Italian, Russian, etc.
- **Asian**: Chinese, Japanese, Korean, Hindi, Arabic, Thai, etc.
- **African**: Swahili, Yoruba, Zulu, etc.
- **Others**: And many more...

See the full list in [all_dataset_labels.json](all_dataset_labels.json).

## 🏗️ Model Architecture

Lark uses a novel byte-level architecture:

1. **Byte Encoder**: Converts raw bytes to contextual representations
2. **Boundary Predictor**: Identifies segment boundaries using Gumbel-Sigmoid
3. **Segment Decoder**: Processes segments for language classification

This architecture enables:
- No vocabulary limitations
- Robust handling of mixed-language text
- Efficient processing of long documents

## 📈 Performance

| Metric | Value |
|--------|-------|
| Overall Accuracy | 90.14% on validation set |
| Inference Speed | ~1ms per text (CPU) |
| Model Size | 9.28MB (float16) |
| Precision | float16 (CPU/GPU compatible) |
| Total Parameters | 4,866,919 |
| Supported Languages | 102 |

### Training Dataset
The model was trained on a comprehensive dataset combining:
- **opus-100** - Multilingual parallel corpus
- **Mike0307/language-detection** - Language detection dataset
- **sirgecko___language_detection** - Language detection dataset
- **papluca/language-identification** - Language identification dataset
- **sirgecko/language_detection_train** - Language detection training data

**Dataset Statistics:**
- Train samples: 109,636,748
- Validation samples: 385,306
- Total languages: 102

### Evaluation Results
Detailed per-language evaluation results (accuracy, precision, recall, F1-score) will be available in the evaluation results file. The model achieves 90.14% overall accuracy on the validation dataset.

**Note on Evaluation Data**: While the model achieves strong overall performance, the current evaluation dataset has limited coverage for some languages (e.g., an, dz, hy, mn, yo). This is due to the validation split not containing samples for these languages. However, the training dataset provides comprehensive coverage.

### Training Dataset Details
The model was trained on a comprehensive dataset combining:
- **OPUS-100** - Multilingual parallel corpus containing 100 language pairs
- **Mike0307/language-detection** - Language detection dataset
- **sirgecko___language_detection** - Language detection dataset
- **papluca/language-identification** - Language identification dataset
- **sirgecko/language_detection_train** - Language detection training data

**OPUS-100 Dataset Statistics:**
- Contains approximately 55 million sentence pairs
- Covers 99 language pairs
- 44 language pairs have 1 million+ sentence pairs
- 73 language pairs have 100,000+ sentence pairs  
- 95 language pairs have 10,000+ sentence pairs
- Each language has at least 10,000 training samples

**Dataset Statistics:**
- Train samples: 109,636,748
- Validation samples: 385,306
- Total languages: 102

## 🔧 API Reference

### LarkDetector Class

```python
class LarkDetector:
    def __init__(self, model_path: str = None, labels_path: str = None):
        """Initialize the language detector"""
    
    def detect(self, text: str) -> Tuple[str, float]:
        """Detect language for single text"""
    
    def detect_batch(self, texts: List[str]) -> List[Tuple[str, float]]:
        """Batch language detection"""
    
    def detect_with_topk(self, text: str, k: int = 5) -> Tuple[str, float, List[Dict]]:
        """Get top-k predictions with probabilities"""
    
    def detect_with_confidence(self, text: str, confidence_threshold: float = 0.5) -> Tuple[str, float, List[Dict]]:
        """Detection with confidence threshold"""
```

## 🛠️ Development

### Setup Development Environment
```bash
git clone https://github.com/farshore-byte/LarkDetect.git
cd LarkDetect
pip install -e ".[dev]"
```

### Running Tests
```bash
python -m pytest tests/
```

### Building from Source
```bash
python setup.py sdist bdist_wheel
```

## 📝 Citation

If you use Lark in your research, please cite:

```bibtex
@software{lark2025,
  title={Lark: Byte-Level Language Detection},
  author={Farshore AI},
  year={2024},
  url={https://github.com/farshore-byte/LarkDetect}
}
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to the open-source community for datasets and tools
- Inspired by modern language detection approaches
- Built with PyTorch and Hugging Face ecosystem
