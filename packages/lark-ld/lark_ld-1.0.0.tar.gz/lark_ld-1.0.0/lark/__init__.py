"""
Lark - Byte-Level Language Detection

A powerful language detection model that supports 102 languages
with byte-level processing and high accuracy.
"""

from .detector import LarkDetector, detect_language
from .model import LarkModel
from .tokenizer import batch_tokenize

__version__ = "1.0.0"
__author__ = "Jiang Chengcheng"
__email__ = "3306065226@qq.com"

__all__ = [
    "LarkDetector",
    "LarkModel", 
    "batch_tokenize",
    "detect_language",
]
