"""
Utility functions for image similarity calculation
"""

import cv2
import imagehash
from PIL import Image


def phash_similarity(img1, img2):
    """
    使用感知哈希计算两张图片相似度
    :param img1: OpenCV BGR数组、PIL Image对象或图片路径
    :param img2: OpenCV BGR数组、PIL Image对象或图片路径
    :return: float - 相似度分数 (0-1)
    """
    def _to_pil_image(img):
        if isinstance(img, str):  # 图片路径
            return Image.open(img).convert("RGB")
        elif hasattr(img, 'shape'):  # OpenCV数组
            return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        else:  # PIL Image
            return img.convert("RGB")

    pil_img1 = _to_pil_image(img1)
    pil_img2 = _to_pil_image(img2)

    hash1 = imagehash.phash(pil_img1)
    hash2 = imagehash.phash(pil_img2)
    similarity = 1 - (hash1 - hash2) / len(hash1.hash)**2
    return float(similarity)


def dino_similarity(img1, img2):
    """
    使用DINO AI模型计算两张图片相似度
    :param img1: OpenCV BGR数组、PIL Image对象或图片路径
    :param img2: OpenCV BGR数组、PIL Image对象或图片路径
    :return: float - 相似度分数 (0-1)
    """
    def _to_pil_image(img):
        if isinstance(img, str):  # 图片路径
            return Image.open(img).convert("RGB")
        elif hasattr(img, 'shape'):  # OpenCV数组
            return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        else:  # PIL Image
            return img.convert("RGB")

    pil_img1 = _to_pil_image(img1)
    pil_img2 = _to_pil_image(img2)

    from .dov import DinoSimilarity
    dino = DinoSimilarity()
    _, similarity_score = dino.is_similar(pil_img1, pil_img2)
    return float(similarity_score)