# Video Intelligent Splitter

Automatically splits videos into segments based on scene changes. Uses traditional hash algorithms + AI model dual verification for precise scene transition detection.

## Features

- **Smart Scene Detection**: Combines phash and DINOv2 model for accurate scene transition identification
- **Dual Verification**: Prevents false positives by filtering subtle changes in similar scenes
- **Flexible Configuration**: Supports custom similarity thresholds, output paths, and other parameters
- **Progress Display**: Real-time processing progress and detection results

## Installation

```bash
pip install opencv-python imagehash pillow numpy torch transformers
```

## Usage

### Basic Usage
```bash
python video_splitter.py input.mp4
```

### Specify Output Directory
```bash
python video_splitter.py input.mp4 -o output_folder
```

### Adjust Parameters
```bash
python video_splitter.py input.mp4 -t 0.85 -m 30 -o segments
```

### Parameters
- `video_path`: Input video file path (required)
- `-o, --output`: Output directory (default: video_segments)
- `-t, --threshold`: Similarity threshold, 0-1 range (default: 0.80)
- `-m, --min-frames`: Minimum segment frames (default: 0)

## Output

The program generates numbered MP4 files in the specified directory:
- `segment_000.mp4`
- `segment_001.mp4`
- `segment_002.mp4`
- ...

## Technical Approach

1. **Fast Screening**: Uses phash algorithm for inter-frame similarity calculation
2. **Precise Verification**: When similarity is below threshold, uses DINOv2 model for secondary confirmation
3. **Smart Filtering**: Only performs segmentation when both detections confirm scene transition

## Project Structure

- `video_splitter.py`: Main program for video splitting functionality
- `dov.py`: DINOv2 similarity calculation module
- `main.py`: Browser automation script (independent feature)