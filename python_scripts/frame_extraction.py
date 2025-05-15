import cv2
import base64
import time
import os
from datetime import datetime

def extract_frames(
    video_path,
    frame_interval=2,  # Now interpreted as seconds of video time
    resize_ratio=0.5,
    compression_quality=50,
    debug=False
):
    # Check if file exists
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Files in directory: {os.listdir('.')}")
        return []

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Cannot open video file {video_path}")
        return []

    # Get video properties for debugging
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count/fps if fps > 0 else 0
    
    print(f"Starting frame extraction from {video_path}")
    print(f"Video properties: {frame_count} frames, {fps:.2f} FPS, {duration:.2f} seconds")

    base64_frames = []  # Store base64-encoded frames here
    frame_number = 0
    
    # Calculate how many frames to skip between captures
    # This converts seconds into equivalent number of frames
    frames_to_skip = int(frame_interval * fps)
    
    # Calculate total expected captures
    expected_captures = frame_count // frames_to_skip if frames_to_skip > 0 else 0
    print(f"Expected to capture approximately {expected_captures} frames (every {frames_to_skip} frames)")

    # For each frame in the video
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print(f"End of video or failed to read frame after {frame_number} frames processed.")
            break

        frame_number += 1
        
        # Only process frames at the specified interval
        if frames_to_skip > 0 and frame_number % frames_to_skip == 0:
            if debug:
                print(f"Processing frame {frame_number}/{frame_count}")
                
            # Resize frame
            if resize_ratio != 1.0:
                height, width = frame.shape[:2]
                new_dims = (int(width * resize_ratio), int(height * resize_ratio))
                frame = cv2.resize(frame, new_dims, interpolation=cv2.INTER_AREA)

            # Compress frame
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), compression_quality]
            success, buffer = cv2.imencode('.jpg', frame, encode_param)
            if not success:
                print("Failed to encode frame.")
                continue

            # Convert to base64
            base64_frame = base64.b64encode(buffer).decode('utf-8')

            # Save to local list
            base64_frames.append(base64_frame)
            
            if debug:
                print(f"Captured frame {len(base64_frames)} (original frame #{frame_number})")

    cap.release()
    print("Finished processing video.")
    print(f"Total frames captured and stored as base64: {len(base64_frames)}")

    return base64_frames


if __name__ == "__main__":
    # Use absolute path for more reliability
    current_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(current_dir, "class-clip.mp4")
    
    print(f"Starting extraction from {video_path}")
    
    # Use frame-based extraction instead of time-based for more reliable results
    frames_as_base64 = extract_frames(
        video_path=video_path,
        frame_interval=10,           # seconds of video time between frame captures
        resize_ratio=0.5,           # scale frame to 50%
        compression_quality=50,     # JPEG quality
        debug=True                  # Enable debug output
    )

    if frames_as_base64:
        # Save to a local file
        output_path = os.path.join(current_dir, "extracted_base64_frames.txt")
        with open(output_path, "w") as f:
            for b64 in frames_as_base64:
                f.write(b64 + "\n")
        print(f"Saved {len(frames_as_base64)} frames to {output_path}")
    else:
        print("No frames were extracted. Check the error messages above.")
