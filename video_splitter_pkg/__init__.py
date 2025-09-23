"""
Video Intelligent Splitter

A Python package for automatically splitting videos into segments based on scene changes.
Uses traditional hash algorithms + AI model dual verification for precise scene transition detection.
"""

from .video_splitter import VideoSplitter
from .dov import DinoSimilarity
from .utils import phash_similarity, dino_similarity

__version__ = "1.0.0"
__author__ = "livoras"
__email__ = ""
__description__ = "Automatically splits videos into segments based on scene changes using AI"

__all__ = ["VideoSplitter", "DinoSimilarity", "phash_similarity", "dino_similarity"]