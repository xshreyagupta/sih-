import cv2
import os

def extract_frames(video_path, output_dir, step=3):
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video at {video_path}")
        return

    count = 0
    saved_count = 0

    while True:
        success, frame = cap.read()

        if not success:
            break

        # Save every 3rd frame
        if count % step == 0:
            frame_name = f"test_video6_frame_{saved_count:04d}.jpg"
            cv2.imwrite(
                os.path.join(output_dir, frame_name),
                frame
            )
            saved_count += 1

        count += 1

    cap.release()

    print(f"Extracted {saved_count} frames to {output_dir}")


if __name__ == "__main__":
    extract_frames(
        "../videos/test_video6.mp4",
        "../data/test_video6_frames",
        step=3
    )