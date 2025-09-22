# pip install transformers pillow faiss-cpu   # 如果有 GPU 可换 faiss-gpu
from transformers import AutoImageProcessor, AutoModel
import torch, faiss, numpy as np
from PIL import Image

class DinoSimilarity:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.proc = AutoImageProcessor.from_pretrained("facebook/dinov2-base", use_fast=True)
        self.model = AutoModel.from_pretrained("facebook/dinov2-base").to(self.device).eval()

    def embed(self, img):
        """返回 L2 归一化后的 1024 维向量 (float32)"""
        if isinstance(img, str):
            img = Image.open(img).convert("RGB")
        inputs = self.proc(images=img, return_tensors="pt").to(self.device)
        with torch.no_grad():
            v = self.model(**inputs).last_hidden_state[:, 0]          # CLS token
        v = torch.nn.functional.normalize(v, dim=1)              # L2
        return v.cpu().numpy().astype('float32')

    def is_similar(self, img1, img2, threshold=0.92):
        """
        判断两张图片是否相似
        :param img1: PIL Image 对象或图片路径
        :param img2: PIL Image 对象或图片路径
        :param threshold: 相似度阈值，默认0.92
        :return: (bool, float) - (是否相似, 相似度)
        """
        v1 = self.embed(img1)
        v2 = self.embed(img2)
        similarity = float(v1 @ v2.T)
        return similarity >= threshold, similarity

# 创建全局实例
dino = DinoSimilarity()

def is_similar(img1, img2, threshold=0.9):
    """
    判断两张图片是否相似的便捷函数
    :param img1: PIL Image 对象或图片路径
    :param img2: PIL Image 对象或图片路径
    :param threshold: 相似度阈值，默认0.92
    :return: (bool, float) - (是否相似, 相似度)
    """
    return dino.is_similar(img1, img2, threshold)

if __name__ == "__main__":
    # 示例用法
    img1_path = "frames3/0624.jpg"
    img2_path = "frames3/0625.jpg"
    
    is_sim, sim_score = is_similar(img1_path, img2_path)
    print(f"相似度: {sim_score:.4f}")
    print(f"判定：{'相似' if is_sim else '不相似'}")
