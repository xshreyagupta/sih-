import cv2
import sys
from pathlib import Path
from ultralytics import YOLO


# ============================================================
# PATHS
# ============================================================

# ~/Desktop/sih-
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ~/Desktop/sih-/SmartRoad-M1
PROJECT_DIR = BASE_DIR / "SmartRoad-M1"

VIDEOS_DIR = PROJECT_DIR / "videos"
OUTPUTS_DIR = PROJECT_DIR / "outputs"


# ============================================================
# MODEL PATHS
# ============================================================

INFRA_MODEL = (
    BASE_DIR
    / "runs"
    / "detect"
    / "runs"
    / "detect"
    / "smartroad_v2_fast"
    / "weights"
    / "best.pt"
)

DEFECT_MODEL = (
    BASE_DIR / "runs" / "runs" / "detect"
    / "road_damage_v2" / "weights" / "best.pt"
)


# ============================================================
# GET VIDEO FROM TERMINAL
# ============================================================

def get_input_video():

    if len(sys.argv) < 2:
        print("\nERROR: Please provide a video filename.")
        print("\nExample:")
        print("python SmartRoad-M1/src/combined_inference.py test_video9.mp4")
        sys.exit(1)

    video_name = sys.argv[1]

    input_video = VIDEOS_DIR / video_name

    if not input_video.exists():
        print(f"\nERROR: Video not found:")
        print(input_video)
        sys.exit(1)

    return input_video


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("SMARTROAD COMBINED INFERENCE")
    print("=" * 60)

    # --------------------------------------------------------
    # Input video
    # --------------------------------------------------------

    input_video = get_input_video()

    output_video = OUTPUTS_DIR / f"combined_{input_video.stem}.mp4"

    print("\nInput video:")
    print(f"  {input_video}")

    print("\nInfrastructure model:")
    print(f"  {INFRA_MODEL}")

    print("\nRoad damage model:")
    print(f"  {DEFECT_MODEL}")

    print("\nOutput:")
    print(f"  {output_video}")

    # --------------------------------------------------------
    # Check models
    # --------------------------------------------------------

    if not INFRA_MODEL.exists():
        print("\nERROR: Infrastructure model not found:")
        print(INFRA_MODEL)
        sys.exit(1)

    if not DEFECT_MODEL.exists():
        print("\nERROR: Road damage model not found:")
        print(DEFECT_MODEL)
        sys.exit(1)

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # Load models
    # --------------------------------------------------------

    print("\nLoading infrastructure model...")
    infra_model = YOLO(str(INFRA_MODEL))

    print("Loading road damage model...")
    defect_model = YOLO(str(DEFECT_MODEL))

    print("Models loaded successfully.")

    # --------------------------------------------------------
    # Open video
    # --------------------------------------------------------

    cap = cv2.VideoCapture(str(input_video))

    if not cap.isOpened():
        print("\nERROR: Could not open video.")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 24

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print("\nVideo information:")
    print(f"  Resolution: {width} x {height}")
    print(f"  FPS: {fps:.2f}")
    print(f"  Frames: {total_frames}")

    # --------------------------------------------------------
    # Output writer
    # --------------------------------------------------------

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    writer = cv2.VideoWriter(
        str(output_video),
        fourcc,
        fps,
        (width, height)
    )

    if not writer.isOpened():
        print("\nERROR: Could not create output video.")
        cap.release()
        sys.exit(1)

    # --------------------------------------------------------
    # Process video
    # --------------------------------------------------------

    frame_number = 0

    print("\nStarting inference...\n")

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        frame_number += 1

        # ====================================================
        # INFRASTRUCTURE MODEL
        # ====================================================

        infra_results = infra_model.predict(
            source=frame,
            conf=0.25,
            device="mps",
            verbose=False
        )

        # ====================================================
        # ROAD DAMAGE MODEL
        # ====================================================

        defect_results = defect_model.predict(
            source=frame,
            conf=0.25,
            device="mps",
            verbose=False
        )

        # Start with original frame
        annotated_frame = frame.copy()

        # ====================================================
        # INFRASTRUCTURE DETECTIONS
        # GREEN BOX
        # ====================================================

        for result in infra_results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist()
                )

                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = infra_model.names[class_id]

                label = f"{class_name} {confidence:.2f}"

                cv2.rectangle(
                    annotated_frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    annotated_frame,
                    label,
                    (x1, max(y1 - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 0),
                    2
                )

        # ====================================================
        # ROAD DAMAGE DETECTIONS
        # RED BOX
        # ====================================================

        for result in defect_results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist()
                )

                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = defect_model.names[class_id]

                label = f"{class_name} {confidence:.2f}"

                cv2.rectangle(
                    annotated_frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 255),
                    2
                )

                cv2.putText(
                    annotated_frame,
                    label,
                    (x1, min(y2 + 20, height - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 0, 255),
                    2
                )

        # ====================================================
        # FRAME NUMBER
        # ====================================================

        cv2.putText(
            annotated_frame,
            f"Frame: {frame_number}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # ====================================================
        # SAVE FRAME
        # ====================================================

        writer.write(annotated_frame)

        # ====================================================
        # PROGRESS
        # ====================================================

        if frame_number % 10 == 0:

            if total_frames > 0:

                progress = (
                    frame_number / total_frames
                ) * 100

                print(
                    f"Processed {frame_number}/{total_frames} "
                    f"({progress:.1f}%)"
                )

        # ====================================================
        # DISPLAY
        # ====================================================

        cv2.imshow(
            "SmartRoad Combined Detection",
            annotated_frame
        )

        # Press Q to stop
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("\nStopped by user.")
            break

    # ========================================================
    # CLEANUP
    # ========================================================

    cap.release()
    writer.release()
    cv2.destroyAllWindows()

    print("\n" + "=" * 60)
    print("INFERENCE COMPLETE")
    print("=" * 60)

    print(f"\nFrames processed: {frame_number}")

    print("\nOutput saved to:")
    print(output_video)


# ==========
# ==================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
