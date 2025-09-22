import cv2
import imagehash
from PIL import Image
import numpy as np
import os
from datetime import datetime
import io
import argparse
from dov import DinoSimilarity

class VideoSplitter:
    def __init__(self, video_path, output_dir, similarity_threshold=0.7, min_segment_frames=0):
        """
        初始化视频分割器
        :param video_path: 输入视频路径
        :param output_dir: 输出目录
        :param similarity_threshold: 相似度阈值，低于此值视为场景切换
        :param min_segment_frames: 最小片段帧数，防止过度分割
        """
        self.video_path = video_path
        self.output_dir = output_dir
        self.similarity_threshold = similarity_threshold
        self.min_segment_frames = min_segment_frames
        self.dino = DinoSimilarity()
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def _calculate_frame_similarity(self, frame1, frame2):
        """计算两帧之间的相似度"""
        # 将OpenCV的BGR图像转换为PIL的RGB图像
        frame1_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
        frame2_rgb = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
        
        # 转换为PIL Image对象
        pil_img1 = Image.fromarray(frame1_rgb)
        pil_img2 = Image.fromarray(frame2_rgb)
        
        # 使用phash替代average_hash，以获得更准确的相似度比较
        hash1 = imagehash.phash(pil_img1)
        hash2 = imagehash.phash(pil_img2)
        
        # 计算相似度
        similarity = 1 - (hash1 - hash2) / len(hash1.hash)**2
        return similarity
        
    def _find_split_points(self, cap):
        """
        分析视频找出分割点
        返回分割点的帧索引列表
        """
        split_points = []
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        ret, prev_frame = cap.read()
        if not ret:
            return split_points
            
        current_frame_idx = 1
        last_split_idx = 0
        
        print(f"开始分析视频帧... 总帧数: {total_frames}")
        
        while True:
            ret, current_frame = cap.read()
            if not ret:
                break
                
            # 第一步：使用 phash 进行初步判断
            similarity = self._calculate_frame_similarity(prev_frame, current_frame)
            
            # 当 phash 相似度低于阈值时，进行 DINO 二次确认
            if similarity < self.similarity_threshold:
                # 转换为 PIL Image 进行 DINO 判断
                prev_frame_rgb = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2RGB)
                current_frame_rgb = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
                prev_pil = Image.fromarray(prev_frame_rgb)
                current_pil = Image.fromarray(current_frame_rgb)

                # 使用 DINO 进行二次判断
                is_sim, dino_similarity = self.dino.is_similar(prev_pil, current_pil)
                
                # 只有当 DINO 也判断不相似时，才添加分割点
                if not is_sim:
                    split_points.append(current_frame_idx)
                    last_split_idx = current_frame_idx
                    print(f"在帧 {current_frame_idx} 处发现场景切换点 (phash相似度: {similarity:.2f}, DINO相似度: {dino_similarity:.2f})")
                else:
                    # prev_pil.show()
                    # current_pil.show()
                    print(f"在帧 {current_frame_idx} 处发现场景切换点 (phash相似度: {similarity:.2f}, DINO相似度: {dino_similarity:.2f}), ignore")
                
            prev_frame = current_frame
            current_frame_idx += 1
            
            # 显示进度
            if current_frame_idx % 100 == 0:
                progress = (current_frame_idx / total_frames) * 100
                print(f"处理进度: {progress:.1f}%")
                
        return split_points
        
    def _save_video_segment(self, cap, start_frame, end_frame, segment_idx):
        """保存视频片段"""
        # 设置输入视频位置到起始帧
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        # 获取视频基本信息
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 创建输出视频写入器
        output_path = os.path.join(self.output_dir, f"segment_{segment_idx:03d}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frames_to_save = end_frame - start_frame
        frames_saved = 0
        
        while frames_saved < frames_to_save:
            ret, frame = cap.read()
            if not ret:
                break
                
            out.write(frame)
            frames_saved += 1
            
        out.release()
        print(f"保存片段 {segment_idx}: {output_path} (帧 {start_frame} 到 {end_frame})")
        
    def process(self):
        """处理视频并保存片段"""
        print(f"开始处理视频: {self.video_path}")
        
        # 打开视频文件
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {self.video_path}")
            
        # 获取视频信息
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"视频信息 - 总帧数: {total_frames}, FPS: {fps}")
        
        # 查找分割点
        split_points = self._find_split_points(cap)
        
        # 添加视频起始和结束点
        split_points = [0] + split_points + [total_frames]
        
        # 保存每个片段
        print(f"\n开始保存视频片段...")
        for i in range(len(split_points) - 1):
            start_frame = split_points[i]
            end_frame = split_points[i + 1]
            self._save_video_segment(cap, start_frame, end_frame, i)
            
        cap.release()
        print(f"\n处理完成！共分割出 {len(split_points) - 1} 个片段")
        
def main():
    parser = argparse.ArgumentParser(description='视频智能分割器 - 基于场景变化自动分割视频')
    parser.add_argument('video_path', help='输入视频文件路径')
    parser.add_argument('-o', '--output', default='video_segments', help='输出目录路径 (默认: video_segments)')
    parser.add_argument('-t', '--threshold', type=float, default=0.80, help='相似度阈值，低于此值视为场景切换 (默认: 0.80)')
    parser.add_argument('-m', '--min-frames', type=int, default=0, help='最小片段帧数，防止过度分割 (默认: 0)')

    args = parser.parse_args()

    # 验证输入文件是否存在
    if not os.path.exists(args.video_path):
        print(f"错误：视频文件不存在: {args.video_path}")
        return

    splitter = VideoSplitter(
        video_path=args.video_path,
        output_dir=args.output,
        similarity_threshold=args.threshold,
        min_segment_frames=args.min_frames
    )

    splitter.process()

if __name__ == "__main__":
    main() 