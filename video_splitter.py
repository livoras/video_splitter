import cv2
import imagehash
from PIL import Image
import numpy as np
import os
import tempfile
from datetime import datetime
import io
import argparse
from dov import DinoSimilarity

class VideoSplitter:
    def __init__(self, video_path, output_dir=None, similarity_threshold=0.7, min_segment_frames=0, progress_callback=None):
        """
        初始化视频分割器
        :param video_path: 输入视频路径
        :param output_dir: 输出目录，为None时只分析不保存
        :param similarity_threshold: 相似度阈值，低于此值视为场景切换
        :param min_segment_frames: 最小片段帧数，防止过度分割
        :param progress_callback: 进度回调函数，接收 (current_frame, total_frames) 参数
        """
        # 验证输入参数
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        if not os.path.isfile(video_path):
            raise ValueError(f"路径不是文件: {video_path}")
        if not 0 <= similarity_threshold <= 1:
            raise ValueError(f"相似度阈值必须在0-1之间: {similarity_threshold}")
        if min_segment_frames < 0:
            raise ValueError(f"最小片段帧数不能为负数: {min_segment_frames}")

        self.video_path = video_path
        self.similarity_threshold = similarity_threshold
        self.min_segment_frames = min_segment_frames
        self.progress_callback = progress_callback
        self.dino = DinoSimilarity()

        # 处理输出目录：如果为None则创建临时目录
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = os.path.join(tempfile.gettempdir(), f"video_segments_{timestamp}")
        else:
            self.output_dir = output_dir

        # 确保输出目录存在
        if self.output_dir and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
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
            
            # 显示进度和回调
            if current_frame_idx % 100 == 0:
                progress = (current_frame_idx / total_frames) * 100
                print(f"处理进度: {progress:.1f}%")
                if self.progress_callback:
                    self.progress_callback(current_frame_idx, total_frames)
                
        return split_points
        
    def _save_video_segment(self, cap, start_frame, end_frame, segment_idx):
        """保存视频片段"""
        if not self.output_dir:
            return

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

        if not out.isOpened():
            raise RuntimeError(f"无法创建输出视频文件: {output_path}")

        try:
            frames_to_save = end_frame - start_frame
            frames_saved = 0

            while frames_saved < frames_to_save:
                ret, frame = cap.read()
                if not ret:
                    break

                out.write(frame)
                frames_saved += 1
        finally:
            out.release()

        print(f"保存片段 {segment_idx}: {output_path} (帧 {start_frame} 到 {end_frame})")
        
    def analyze(self):
        """分析视频并返回分割点信息，不保存文件"""
        print(f"开始分析视频: {self.video_path}")

        # 打开视频文件
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {self.video_path}")

        try:
            # 获取视频信息
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0

            print(f"视频信息 - 总帧数: {total_frames}, FPS: {fps}, 时长: {duration:.2f}s")

            # 查找分割点
            split_points = self._find_split_points(cap)

            # 添加视频起始和结束点
            full_split_points = [0] + split_points + [total_frames]

            # 构建返回信息
            segments = []
            for i in range(len(full_split_points) - 1):
                start_frame = full_split_points[i]
                end_frame = full_split_points[i + 1]
                start_time = start_frame / fps if fps > 0 else 0
                end_time = end_frame / fps if fps > 0 else 0

                # 构建文件路径
                file_path = None
                if self.output_dir:
                    file_path = os.path.join(self.output_dir, f"segment_{i:03d}.mp4")

                segments.append({
                    'index': i,
                    'start_frame': start_frame,
                    'end_frame': end_frame,
                    'start_time': start_time,
                    'end_time': end_time,
                    'frame_count': end_frame - start_frame,
                    'file_path': file_path
                })

            result = {
                'video_path': self.video_path,
                'output_dir': self.output_dir,
                'total_frames': total_frames,
                'fps': fps,
                'duration': duration,
                'split_points': split_points,
                'segments': segments,
                'segment_count': len(segments)
            }

            print(f"\n分析完成！共检测到 {len(split_points)} 个分割点，{len(segments)} 个片段")
            return result

        finally:
            cap.release()

    def process(self, save_files=True):
        """处理视频，可选择是否保存文件"""
        result = self.analyze()

        if save_files and self.output_dir:
            print(f"\n开始保存视频片段到: {self.output_dir}")

            # 重新打开视频文件进行保存
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                raise ValueError(f"无法打开视频文件: {self.video_path}")

            try:
                for segment in result['segments']:
                    self._save_video_segment(
                        cap,
                        segment['start_frame'],
                        segment['end_frame'],
                        segment['index']
                    )
            finally:
                cap.release()

            print(f"\n保存完成！共保存了 {result['segment_count']} 个片段")

        return result
        
def main():
    parser = argparse.ArgumentParser(description='视频智能分割器 - 基于场景变化自动分割视频')
    parser.add_argument('video_path', help='输入视频文件路径')
    parser.add_argument('-o', '--output', default='video_segments', help='输出目录路径 (默认: video_segments)')
    parser.add_argument('-t', '--threshold', type=float, default=0.80, help='相似度阈值，低于此值视为场景切换 (默认: 0.80)')
    parser.add_argument('-m', '--min-frames', type=int, default=0, help='最小片段帧数，防止过度分割 (默认: 0)')

    args = parser.parse_args()

    try:
        splitter = VideoSplitter(
            video_path=args.video_path,
            output_dir=args.output,
            similarity_threshold=args.threshold,
            min_segment_frames=args.min_frames
        )

        splitter.process()

    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"错误: {e}")
        return 1
    except Exception as e:
        print(f"未知错误: {e}")
        return 1

    return 0

if __name__ == "__main__":
    main() 