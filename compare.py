import imagehash
from PIL import Image
from pathlib import Path

# 颜色常量
RED = '\033[91m'
RESET = '\033[0m'

def compare_adjacent_frames(frames_dir, similarity_threshold=0.7):
    """比较相邻帧之间的相似度"""
    # 获取所有jpg文件并按数字排序
    image_files = sorted(
        Path(frames_dir).glob('*.jpg'),
        key=lambda x: int(x.stem)  # 使用文件名中的数字进行排序
    )
    
    # 比较相邻图片
    for img1_path, img2_path in zip(image_files, image_files[1:]):
        try:
            img1 = Image.open(img1_path)
            img2 = Image.open(img2_path)
            
            hash1 = imagehash.phash(img1)
            hash2 = imagehash.phash(img2)
            
            similarity = 1 - (hash1 - hash2) / len(hash1.hash)**2
            
            # 根据相似度决定输出颜色
            color = RED if similarity < similarity_threshold else ''
            print(f"{color}{img1_path.name} 与 {img2_path.name} 的相似度: {similarity:.2f}{RESET}")
            
        except Exception as e:
            print(f"{RED}处理图片对 {img1_path.name} - {img2_path.name} 时出错: {e}{RESET}")

if __name__ == "__main__":
    frames_dir = "frames3"
    compare_adjacent_frames(frames_dir)
