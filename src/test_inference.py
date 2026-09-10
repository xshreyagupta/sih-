import cv2
from ultralytics import YOLO

def test_video_inference():
    # 1. Load your 1-epoch trained model
    model = YOLO("../runs/detect/india_test/weights/best.pt")

    # 2. Open the input video
    video_path = "../videos/road.mp4"
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video at {video_path}")
        return

    # 3. Set up the VideoWriter to save the annotated output
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_path = "../outputs/annotated_road.mp4"
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    print(f"Starting inference on {video_path}...")
    print("Press 'q' in the video window to stop early.")

    # 4. Process the video frame by frame
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Run YOLO inference
        results = model.predict(frame, conf=0.25, verbose=False)

        # Draw bounding boxes and labels
        annotated_frame = results[0].plot()

        # Save and display
        out.write(annotated_frame)
        cv2.imshow("SmartRoad - 1-Epoch Test", annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 5. Clean up
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Done! Video saved to: {output_path}")

if __name__ == "__main__":
    test_video_inference()