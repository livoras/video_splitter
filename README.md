# Video Intelligent Splitter

Automatically splits videos into segments based on scene changes. Uses traditional hash algorithms + AI model dual verification for precise scene transition detection.

## Features

- **Smart Scene Detection**: Combines phash and DINOv2 model for accurate scene transition identification
- **Dual Verification**: Prevents false positives by filtering subtle changes in similar scenes
- **Auto Temp Directory**: Creates timestamped directories when no output path specified
- **Programmatic API**: Use as Python library with detailed results and progress callbacks
- **Similarity Functions**: Standalone image similarity comparison using phash or DINO AI
- **Flexible Configuration**: Supports custom similarity thresholds and parameters

## Installation

### From GitHub (Recommended)
```bash
pip install git+https://github.com/livoras/video_splitter.git
```

### Manual Dependencies (if needed)
```bash
pip install opencv-python imagehash pillow numpy torch transformers
```

## Usage

### API Usage (Recommended)
```python
from video_splitter import VideoSplitter

# Simplest usage - auto temp directory
splitter = VideoSplitter("video.mp4")
result = splitter.process()
print(f"Files saved to: {result['output_dir']}")

# With progress callback
def on_progress(current, total):
    print(f"Progress: {current}/{total}")

splitter = VideoSplitter("video.mp4", progress_callback=on_progress)
result = splitter.process()

# Analysis only (no file output)
result = splitter.analyze()
for segment in result['segments']:
    print(f"Segment {segment['index']}: {segment['file_path']}")
```

### Similarity Functions
```python
from video_splitter_pkg import phash_similarity, dino_similarity

# Compare two images using perceptual hash
score1 = phash_similarity("image1.jpg", "image2.jpg")
print(f"Perceptual hash similarity: {score1:.4f}")

# Compare using AI model (more accurate)
score2 = dino_similarity("image1.jpg", "image2.jpg")
print(f"DINO AI similarity: {score2:.4f}")

# Support multiple input types
from PIL import Image
import cv2

img1 = Image.open("photo1.jpg")           # PIL Image
img2 = cv2.imread("photo2.jpg")           # OpenCV array
path = "photo3.jpg"                       # File path

# All input types work
similarity = phash_similarity(img1, img2)
similarity = dino_similarity(img2, path)
```

### Command Line Usage
```bash
# Auto temp directory
python video_splitter.py input.mp4

# Specify output directory
python video_splitter.py input.mp4 -o output_folder

# Adjust parameters
python video_splitter.py input.mp4 -t 0.85 -m 30
```

### Parameters
- `video_path`: Input video file path (required)
- `output_dir`: Output directory (default: auto temp directory)
- `similarity_threshold`: Similarity threshold, 0-1 range (default: 0.80)
- `progress_callback`: Function to monitor progress (API only)

### Similarity Functions Parameters
- `phash_similarity(img1, img2)`: Fast perceptual hash comparison
- `dino_similarity(img1, img2)`: AI-based semantic similarity
- **Input types**: File paths, PIL Images, or OpenCV arrays
- **Returns**: Float similarity score (0-1, higher = more similar)

## Output

### Files
Generated MP4 files in output directory:
- `segment_000.mp4`, `segment_001.mp4`, `segment_002.mp4`...

### API Results
```python
{
    'video_path': 'input.mp4',
    'output_dir': '/tmp/video_segments_20250922_170046',
    'total_frames': 748,
    'fps': 30.0,
    'duration': 24.93,
    'segment_count': 21,
    'segments': [
        {
            'index': 0,
            'file_path': '/tmp/.../segment_000.mp4',
            'start_frame': 0, 'end_frame': 66,
            'start_time': 0.0, 'end_time': 2.2,
            'frame_count': 66
        }
    ]
}
```

## Technical Approach

1. **Fast Screening**: Uses phash algorithm for inter-frame similarity calculation
2. **Precise Verification**: When similarity is below threshold, uses DINOv2 model for secondary confirmation
3. **Smart Filtering**: Only performs segmentation when both detections confirm scene transition

## Project Structure

- `video_splitter.py`: Main program for video splitting functionality
- `dov.py`: DINOv2 similarity calculation module