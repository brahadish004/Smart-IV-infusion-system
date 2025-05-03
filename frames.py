import cv2
import glob
import os

DATASET_PATH = r"C:\Users\chitr\Pictures\Camera Roll\source2"  # Update with your path

FRAME_OUTPUT_DIR = os.path.join(DATASET_PATH, 'frames2')
os.makedirs(FRAME_OUTPUT_DIR, exist_ok=True)

# Get all video files in sorted order
video_files = sorted(glob.glob(os.path.join(DATASET_PATH, '*.mp4')))

if not video_files:
    print("No videos found in the dataset path.")
    exit()

for video in video_files:
    vidcap = cv2.VideoCapture(video)
    if not vidcap.isOpened():
        print(f"Error: Could not open {video}")
        continue

    # Get video properties
    frame_rate = int(vidcap.get(cv2.CAP_PROP_FPS))  # FPS
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))  # Total frames
    frame_interval = max(1, frame_rate // 1)  # Extract every 1/4 second

    frame_width = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Width
    frame_height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Height

    frame_count = 0
    extracted_count = 0
    success, image = vidcap.read()

    while success:
        if frame_count % frame_interval == 0:
            # ✅ **Check if rotation is needed**
            if frame_width > frame_height:  
                try:
                    rotate_flag = int(vidcap.get(cv2.CAP_PROP_ORIENTATION_META))  # Get rotation metadata
                    if rotate_flag == 90:
                        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                    elif rotate_flag == 180:
                        image = cv2.rotate(image, cv2.ROTATE_180)
                    elif rotate_flag == 270:
                        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                except:
                    pass  # Some OpenCV versions don't support CAP_PROP_ORIENTATION_META

            # Save frame **without forcing rotation**
            frame_name = f"{os.path.basename(video).split('.')[0]}_frame_{extracted_count:05d}.jpg"
            frame_path = os.path.join(FRAME_OUTPUT_DIR, frame_name)
            cv2.imwrite(frame_path, image)  # ✅ Save frame
            extracted_count += 1

        success, image = vidcap.read()
        frame_count += 1

    vidcap.release()
    print(f"Extracted {extracted_count} frames from {video}")

print(f"Frames saved in {FRAME_OUTPUT_DIR}")
