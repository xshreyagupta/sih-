
import cv2
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

from ultralytics import YOLO


# ============================================================
# PROJECT PATHS
# ============================================================

# Project root = SmartRoad-M1
PROJECT_ROOT = Path(__file__).resolve().parent.parent

VIDEOS_DIR = PROJECT_ROOT / "videos"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# MODEL PATHS
# ============================================================

ROAD_MODEL_PATH = (
    PROJECT_ROOT.parent
    / "runs"
    / "runs"
    / "detect"
    / "road_damage_v2"
    / "weights"
    / "best.pt"
)
INFRASTRUCTURE_MODEL_PATH = (
    PROJECT_ROOT.parent
    / "runs"
    / "detect"
    / "runs"
    / "detect"
    / "infrastructure_model_retrain"
    / "weights"
    / "best.pt"
)

# Vehicle model
VEHICLE_MODEL_PATH = PROJECT_ROOT / "yolov8n.pt"


# ============================================================
# CHECK MODEL FILES
# ============================================================

print("\nChecking model files...")

if not ROAD_MODEL_PATH.exists():
    print("ERROR: Road damage model not found:")
    print(ROAD_MODEL_PATH)
    sys.exit(1)

if not INFRASTRUCTURE_MODEL_PATH.exists():
    print("ERROR: Infrastructure model not found:")
    print(INFRASTRUCTURE_MODEL_PATH)
    sys.exit(1)

if not VEHICLE_MODEL_PATH.exists():
    print("ERROR: Vehicle model not found:")
    print(VEHICLE_MODEL_PATH)
    sys.exit(1)


print("Road damage model      :", ROAD_MODEL_PATH)
print("Infrastructure model  :", INFRASTRUCTURE_MODEL_PATH)
print("Vehicle model         :", VEHICLE_MODEL_PATH)


# ============================================================
# LOAD MODELS
# ============================================================

print("\nLoading models...")

road_model = YOLO(str(ROAD_MODEL_PATH))

infrastructure_model = YOLO(
    str(INFRASTRUCTURE_MODEL_PATH)
)

vehicle_model = YOLO(
    str(VEHICLE_MODEL_PATH)
)

print("Models loaded successfully.")


# ============================================================
# VEHICLE CLASSES
# ============================================================

vehicle_classes = {
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}


# ============================================================
# PROCESS ONE VIDEO
# ============================================================

def process_video(video_path):

    video_path = Path(video_path)

    print("\n")
    print("=" * 70)
    print("PROCESSING VIDEO")
    print("=" * 70)
    print("Input:", video_path)

    if not video_path.exists():
        print("ERROR: Video not found:", video_path)
        return

    # --------------------------------------------------------
    # Open video
    # --------------------------------------------------------

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        print("ERROR: Could not open video.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        print("ERROR: Could not determine video FPS.")
        cap.release()
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    duration = total_frames / fps

    print("FPS:", fps)
    print("Resolution:", width, "x", height)
    print("Total frames:", total_frames)
    print("Duration:", round(duration, 2), "seconds")

    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    start_time = datetime.now().astimezone()

    print(
        "Detection start time:",
        start_time.isoformat()
    )

    # --------------------------------------------------------
    # Output filenames
    # --------------------------------------------------------

    video_name = video_path.stem

    output_video = (
        OUTPUTS_DIR
        / f"{video_name}_detection.mp4"
    )

    output_json = (
        OUTPUTS_DIR
        / f"{video_name}_detections.json"
    )

    # --------------------------------------------------------
    # Video writer
    # --------------------------------------------------------

    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )

    out = cv2.VideoWriter(
        str(output_video),
        fourcc,
        fps,
        (width, height)
    )

    if not out.isOpened():
        print("ERROR: Could not create output video.")
        cap.release()
        return

    # --------------------------------------------------------
    # Detection storage
    # --------------------------------------------------------

    events = []

    frame_id = 0

    # ========================================================
    # PROCESS FRAMES
    # ========================================================

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        # ----------------------------------------------------
        # Timestamp
        # ----------------------------------------------------

        timestamp_ms = int(
            (frame_id / fps) * 1000
        )

        real_timestamp = (
            start_time
            + timedelta(milliseconds=timestamp_ms)
        )

        timestamp = real_timestamp.isoformat()

        # ====================================================
        # 1. ROAD DAMAGE MODEL
        # ====================================================

        road_results = road_model(
            frame,
            verbose=False,
            device="mps"
        )

        for result in road_results:

            for box in result.boxes:

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                class_name = road_model.names[
                    class_id
                ]

                # Save event
                events.append({
                    "class_id": class_id,
                    "type": class_name,
                    "source": "road_damage",
                    "confidence": round(
                        confidence,
                        4
                    ),
                    "frame_id": frame_id,
                    "timestamp_ms": timestamp_ms,
                    "timestamp": timestamp,
                    "bbox": [
                        x1,
                        y1,
                        x2,
                        y2
                    ]
                })

                # Draw box
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                label = (
                    f"{class_name} "
                    f"{confidence:.2f}"
                )

                cv2.putText(
                    frame,
                    label,
                    (
                        x1,
                        max(y1 - 10, 20)
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

        # ====================================================
        # 2. INFRASTRUCTURE MODEL
        # ====================================================

        infrastructure_results = (
            infrastructure_model(
                frame,
                verbose=False,
                device="mps"
            )
        )

        for result in infrastructure_results:

            for box in result.boxes:

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                class_name = (
                    infrastructure_model.names[
                        class_id
                    ]
                )

                # Save event
                events.append({
                    "class_id": class_id,
                    "type": class_name,
                    "source": "infrastructure",
                    "confidence": round(
                        confidence,
                        4
                    ),
                    "frame_id": frame_id,
                    "timestamp_ms": timestamp_ms,
                    "timestamp": timestamp,
                    "bbox": [
                        x1,
                        y1,
                        x2,
                        y2
                    ]
                })

                # Draw box
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (255, 0, 0),
                    2
                )

                label = (
                    f"{class_name} "
                    f"{confidence:.2f}"
                )

                cv2.putText(
                    frame,
                    label,
                    (
                        x1,
                        max(y1 - 10, 20)
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 0, 0),
                    2
                )

        # ====================================================
        # 3. VEHICLE MODEL
        # ====================================================

        vehicle_results = vehicle_model(
            frame,
            verbose=False,
            device="mps"
        )

        for result in vehicle_results:

            for box in result.boxes:

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                # Only keep vehicle classes
                if class_id not in vehicle_classes:
                    continue

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                vehicle_type = (
                    vehicle_classes[class_id]
                )

                # Save event
                events.append({
                    "class_id": class_id,
                    "type": vehicle_type,
                    "source": "vehicle",
                    "confidence": round(
                        confidence,
                        4
                    ),
                    "frame_id": frame_id,
                    "timestamp_ms": timestamp_ms,
                    "timestamp": timestamp,
                    "bbox": [
                        x1,
                        y1,
                        x2,
                        y2
                    ]
                })

                # Draw box
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 255),
                    2
                )

                label = (
                    f"{vehicle_type} "
                    f"{confidence:.2f}"
                )

                cv2.putText(
                    frame,
                    label,
                    (
                        x1,
                        max(y1 - 10, 20)
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2
                )

        # ====================================================
        # SAVE FRAME
        # ====================================================

        out.write(frame)

        frame_id += 1

        # Progress
        if frame_id % 100 == 0:

            if total_frames > 0:

                progress = (
                    frame_id
                    / total_frames
                    * 100
                )

                print(
                    f"\rProgress: "
                    f"{progress:.1f}% "
                    f"({frame_id}/{total_frames})",
                    end=""
                )

    # ========================================================
    # CLEANUP
    # ========================================================

    cap.release()
    out.release()

    # ========================================================
    # SAVE JSON
    # ========================================================

    with open(
        output_json,
        "w"
    ) as f:

        json.dump(
            events,
            f,
            indent=2
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n")
    print("-" * 70)
    print("VIDEO COMPLETE")
    print("-" * 70)

    print("Input video:")
    print(video_path)

    print("\nOutput video:")
    print(output_video)

    print("\nOutput JSON:")
    print(output_json)

    print("\nTotal detections:")
    print(len(events))

    # Detection count by source
    road_count = sum(
        1 for event in events
        if event["source"] == "road_damage"
    )

    infrastructure_count = sum(
        1 for event in events
        if event["source"] == "infrastructure"
    )

    vehicle_count = sum(
        1 for event in events
        if event["source"] == "vehicle"
    )

    print("\nDetection breakdown:")
    print("Road damage     :", road_count)
    print("Infrastructure  :", infrastructure_count)
    print("Vehicles        :", vehicle_count)

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

if len(sys.argv) != 2:

    print("\nUsage:")
    print(
        "  python src/detect.py <video>"
    )
    print(
        "  python src/detect.py <folder>"
    )

    print("\nExamples:")
    print(
        "  python src/detect.py videos/test_video5.mp4"
    )

    print(
        "  python src/detect.py videos"
    )

    sys.exit(1)


input_path = Path(sys.argv[1])

# Convert relative path to absolute path
if not input_path.is_absolute():
    input_path = PROJECT_ROOT / input_path


# ============================================================
# SINGLE VIDEO
# ============================================================

if input_path.is_file():

    if input_path.suffix.lower() != ".mp4":

        print(
            "ERROR: Please provide an MP4 video."
        )
        sys.exit(1)

    process_video(input_path)


# ============================================================
# ALL VIDEOS IN FOLDER
# ============================================================

elif input_path.is_dir():

    videos = sorted(
        input_path.glob("*.mp4")
    )

    if len(videos) == 0:

        print(
            "No .mp4 videos found in:"
        )
        print(input_path)

        sys.exit(1)

    print("\n")
    print("=" * 70)
    print("BATCH VIDEO DETECTION")
    print("=" * 70)

    print(
        f"Found {len(videos)} video(s):"
    )

    for video in videos:
        print(" -", video.name)

    print("=" * 70)

    for index, video in enumerate(
        videos,
        start=1
    ):

        print(
            f"\n\nVIDEO {index}/{len(videos)}"
        )

        process_video(video)

    print("\n")
    print("=" * 70)
    print("ALL VIDEOS PROCESSED")
    print("=" * 70)

    print("Results are in:")
    print(OUTPUTS_DIR)


# ============================================================
# INVALID PATH
# ============================================================

else:

    print(
        "ERROR: File or folder not found:"
    )
    print(input_path)

    sys.exit(1)

