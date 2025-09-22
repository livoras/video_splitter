import cv2
import os

def extract_frames(video_path, output_dir):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 打开视频文件
    video = cv2.VideoCapture(video_path)
    
    # 获取一些视频信息
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    
    print(f"开始处理视频...")
    print(f"总帧数: {total_frames}")
    print(f"FPS: {fps}")
    
    frame_count = 0
    while True:
        # 读取一帧
        success, frame = video.read()
        if not success:
            break
            
        # 生成输出文件名（4位数字）
        output_path = os.path.join(output_dir, f"{frame_count:04d}.jpg")
        
        # 保存帧
        cv2.imwrite(output_path, frame)
        
        frame_count += 1
        if frame_count % 100 == 0:
            print(f"已处理 {frame_count} 帧...")
    
    video.release()
    print(f"处理完成！共保存了 {frame_count} 帧")

if __name__ == "__main__":
    video_path = "images/video3.mp4"
    output_dir = "frames3"
    extract_frames(video_path, output_dir)
