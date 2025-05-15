import cv2
import base64
import os
from datetime import datetime
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config( 
    cloud_name = "dzqtx9kms", 
    api_key = os.environ.get("CLOUDINARY_API_KEY"),
    api_secret = os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

# ---------- Function to Upload to Cloudinary ----------
def upload_image_to_cloudinary(base64_image, public_id=None):
    """
    Upload a base64 image to Cloudinary.

    Args:
        base64_image (str): Base64 encoded image string (no data URI prefix)
        public_id (str): Optional public ID for naming the image in Cloudinary

    Returns:
        str: Secure URL of uploaded image if successful, else None
    """
    try:
        upload_result = cloudinary.uploader.upload(
            f"data:image/jpeg;base64,{base64_image}",
            public_id=public_id,
            overwrite=True
        )
        return upload_result["secure_url"]
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        return None

# ---------- Frame Extraction Function ----------
def extract_frames(video_path, frame_interval=2, resize_ratio=0.5, compression_quality=50, debug=False):
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return []

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Cannot open video file {video_path}")
        return []

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0
    frames_to_skip = int(frame_interval * fps)

    print(f"Video: {frame_count} frames, {fps:.2f} FPS, {duration:.2f}s duration")
    print(f"Capturing every {frames_to_skip} frames...")

    frame_number = 0
    captured = 0
    uploaded_urls = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_number += 1
        if frames_to_skip > 0 and frame_number % frames_to_skip == 0:
            if resize_ratio != 1.0:
                height, width = frame.shape[:2]
                new_dims = (int(width * resize_ratio), int(height * resize_ratio))
                frame = cv2.resize(frame, new_dims, interpolation=cv2.INTER_AREA)

            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), compression_quality]
            success, buffer = cv2.imencode('.jpg', frame, encode_param)
            if not success:
                print("Failed to encode frame.")
                continue

            base64_frame = base64.b64encode(buffer).decode('utf-8')
            public_id = f"frame_{frame_number}"

            print(f"Uploading frame {frame_number} to Cloudinary...")
            url = upload_image_to_cloudinary(base64_frame, public_id)
            if url:
                uploaded_urls.append(url)
                captured += 1
                print(f"Uploaded to: {url}")
            else:
                print("Upload failed.")

    cap.release()
    print(f"✅ Finished. Uploaded {captured} frames.")
    return uploaded_urls

# ---------- Main Execution ----------
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(current_dir, "class-clip.mp4")

    print(f"🎞️ Starting extraction from: {video_path}")
    uploaded_frame_urls = extract_frames(
        video_path=video_path,
        frame_interval=30,  # seconds between captures
        resize_ratio=0.5,
        compression_quality=50,
        debug=True
    )

    if uploaded_frame_urls:
        output_file = os.path.join(current_dir, "cloudinary_frame_urls.txt")
        with open(output_file, "w") as f:
            for url in uploaded_frame_urls:
                f.write(url + "\n")
        print(f"🔗 Frame URLs saved to: {output_file}")
    else:
        print("⚠️ No frames uploaded.")
