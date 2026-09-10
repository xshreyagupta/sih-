import json
from pathlib import Path
from collections import defaultdict

import numpy as np
import supervision as sv


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

M1_INPUT_FILE = BASE_DIR / "m1_output" / "final_output1_detections.json"

M3_OUTPUT_FILE = BASE_DIR / "tracking" / "m2_output_m3.json"
M5_OUTPUT_FILE = BASE_DIR / "tracking" / "m2_output_m5.json"


# ============================================================
# CONFIGURATION
# ============================================================

# Horizontal virtual counting line
LINE_Y = 400

# Margin around the counting line
COUNTING_MARGIN = 5


# ============================================================
# VEHICLE CLASSES
# ============================================================

VEHICLE_CLASSES = {
    "car",
    "bus",
    "truck",
    "motorcycle",
    "bicycle",
}


# ============================================================
# INFRASTRUCTURE CLASSES
# ============================================================

INFRASTRUCTURE_CLASSES = {
    "no_horn_sign",
    "no_parking_sign",
    "object",
    "pedestrian_crossing_sign",
    "road_divider",
    "road_work_ahead_sign",
    "school_ahead_sign",
    "speed_limit_sign",
    "stop_sign",
    "streetlight",
    "traffic_light",
    "zebra_crossing",
}


# ============================================================
# ROAD DAMAGE CLASSES
# ============================================================

ROAD_DAMAGE_CLASSES = {
    "Potholes",
    "alligator crack",
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def make_json_safe(value):
    """
    Convert NumPy values into normal Python values
    so json.dump() can save them.
    """

    if isinstance(value, np.ndarray):
        return value.tolist()

    if isinstance(value, np.generic):
        return value.item()

    if isinstance(value, dict):
        return {
            str(key): make_json_safe(val)
            for key, val in value.items()
        }

    if isinstance(value, list):
        return [
            make_json_safe(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            make_json_safe(item)
            for item in value
        ]

    return value


def is_vehicle(class_name):
    return class_name in VEHICLE_CLASSES


def get_bottom_center(bbox):
    """
    bbox = [x1, y1, x2, y2]

    Returns:
        center_x
        bottom_y
    """

    x1, y1, x2, y2 = bbox

    center_x = (x1 + x2) / 2.0
    bottom_y = y2

    return center_x, bottom_y


# ============================================================
# START
# ============================================================

print("=" * 70)
print("M2 TRACKING MODULE")
print("=" * 70)


# ============================================================
# CHECK M1 INPUT
# ============================================================

print("\nM1 input file:")
print(M1_INPUT_FILE)


if not M1_INPUT_FILE.exists():

    raise FileNotFoundError(
        f"\nM1 input file was not found:\n{M1_INPUT_FILE}"
    )


# ============================================================
# LOAD M1 JSON
# ============================================================

with open(
    M1_INPUT_FILE,
    "r",
    encoding="utf-8"
) as file:

    m1_detections = json.load(file)


if not isinstance(m1_detections, list):

    raise ValueError(
        "M1 JSON must contain a list of detections."
    )


print(
    f"\nTotal detections: {len(m1_detections)}"
)


# ============================================================
# GROUP M1 DETECTIONS BY FRAME
# ============================================================

detections_by_frame = defaultdict(list)


for detection in m1_detections:

    required_fields = [
        "class_id",
        "type",
        "source",
        "confidence",
        "frame_id",
        "timestamp_ms",
        "bbox",
    ]


    missing_fields = [
        field
        for field in required_fields
        if field not in detection
    ]


    if missing_fields:

        print(
            "\nWARNING: Detection missing fields:"
            f" {missing_fields}"
        )

        print(detection)

        continue


    frame_id = int(
        detection["frame_id"]
    )


    detections_by_frame[frame_id].append(
        detection
    )


if not detections_by_frame:

    raise ValueError(
        "No valid M1 detections found."
    )


# ============================================================
# FRAME RANGE
# ============================================================

first_frame = min(
    detections_by_frame.keys()
)

last_frame = max(
    detections_by_frame.keys()
)


# Process every frame, including frames
# that contain no detections.
frame_ids = range(
    first_frame,
    last_frame + 1
)


total_frames = (
    last_frame - first_frame + 1
)


print(
    f"Total frames: {total_frames}"
)


# ============================================================
# COUNTING CONFIGURATION
# ============================================================

print("\nCounting line:")
print(
    f"HORIZONTAL Y = {LINE_Y}"
)

print("\nCounting margin:")
print(
    f"{COUNTING_MARGIN} pixels"
)

print("\nCounting method:")
print(
    "BOTTOM OF BBOX CROSSING"
)


print("\n" + "=" * 70)


# ============================================================
# CREATE BYTE TRACKERS
# ============================================================

# Separate tracker for each source/class.
#
# Example:
# ("vehicle", "car")
# ("vehicle", "bus")
# ("infrastructure", "stop_sign")
#
# This follows the current M2 design.

trackers = {}


for class_name in VEHICLE_CLASSES:

    trackers[
        ("vehicle", class_name)
    ] = sv.ByteTrack()


for class_name in INFRASTRUCTURE_CLASSES:

    trackers[
        ("infrastructure", class_name)
    ] = sv.ByteTrack()


for class_name in ROAD_DAMAGE_CLASSES:

    trackers[
        ("road_damage", class_name)
    ] = sv.ByteTrack()


# ============================================================
# GLOBAL TRACKING ID MANAGEMENT
# ============================================================

next_global_id = 1

global_id_map = {}


def get_global_id(
    source,
    class_name,
    byte_track_id
):

    global next_global_id

    key = (
        source,
        class_name,
        int(byte_track_id)
    )


    if key not in global_id_map:

        global_id_map[key] = (
            next_global_id
        )

        next_global_id += 1


    return global_id_map[key]


# ============================================================
# PREVIOUS POSITION DATA
# ============================================================

# Used for speed estimation.

previous_speed_positions = {}


# Used ONLY for counting line crossing.

previous_count_positions = {}


# ============================================================
# COUNTING DATA
# ============================================================

counted_vehicle_ids = set()

total_vehicle_count = 0


# ============================================================
# SPEED DATA
# ============================================================

all_speed_values = []


# ============================================================
# CONGESTION DATA
# ============================================================

congestion_streak = 0


# ============================================================
# OUTPUT DATA
# ============================================================

m3_frames = []

m5_frames = []


# ============================================================
# PROCESS EACH FRAME
# ============================================================

for frame_id in frame_ids:


    # --------------------------------------------------------
    # Get detections for this frame
    # --------------------------------------------------------

    frame_detections = detections_by_frame.get(
        frame_id,
        []
    )


    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    timestamp_ms = 0

    timestamp = None


    if frame_detections:

        timestamp_ms = int(
            frame_detections[0].get(
                "timestamp_ms",
                0
            )
        )

        timestamp = (
            frame_detections[0].get(
                "timestamp"
            )
        )


    # --------------------------------------------------------
    # Group detections by source + class
    # --------------------------------------------------------

    grouped_detections = defaultdict(list)


    for detection in frame_detections:

        source = detection["source"]

        class_name = detection["type"]


        grouped_detections[
            (source, class_name)
        ].append(
            detection
        )


    # --------------------------------------------------------
    # Objects tracked in current frame
    # --------------------------------------------------------

    tracked_objects = []


    # Vehicle speeds in current frame

    current_vehicle_speeds = []


    # ========================================================
    # RUN BYTE TRACK ON EACH GROUP
    # ========================================================

    for (
        source,
        class_name
    ), group in grouped_detections.items():


        tracker_key = (
            source,
            class_name
        )


        # Ignore unknown groups

        if tracker_key not in trackers:

            continue


        tracker = trackers[
            tracker_key
        ]


        # ----------------------------------------------------
        # Build XYXY array
        # ----------------------------------------------------

        xyxy = []


        confidence_values = []


        for detection in group:

            bbox = detection["bbox"]


            # Ensure exactly four values

            if len(bbox) != 4:

                continue


            xyxy.append(
                [
                    float(bbox[0]),
                    float(bbox[1]),
                    float(bbox[2]),
                    float(bbox[3]),
                ]
            )


            confidence_values.append(
                float(
                    detection["confidence"]
                )
            )


        # No valid bounding boxes

        if not xyxy:

            continue


        # ----------------------------------------------------
        # IMPORTANT FIX
        #
        # Supervision requires NumPy ndarray
        # with shape (N, 4)
        # ----------------------------------------------------

        xyxy_array = np.asarray(
            xyxy,
            dtype=np.float32
        )


        confidence_array = np.asarray(
            confidence_values,
            dtype=np.float32
        )


        # Safety check

        if (
            xyxy_array.ndim != 2
            or xyxy_array.shape[1] != 4
        ):

            print(
                "\nWARNING: Invalid bbox shape:"
                f" {xyxy_array.shape}"
            )

            continue


        # ----------------------------------------------------
        # Create Supervision detections
        # ----------------------------------------------------

        detections_sv = sv.Detections(
            xyxy=xyxy_array,
            confidence=confidence_array,
        )


        # ----------------------------------------------------
        # Update ByteTrack
        # ----------------------------------------------------

        tracked = tracker.update_with_detections(
            detections_sv
        )


        # ----------------------------------------------------
        # Process tracked detections
        # ----------------------------------------------------

        if tracked.tracker_id is None:

            continue


        for index in range(
            len(tracked)
        ):


            byte_track_id = (
                tracked.tracker_id[index]
            )


            if byte_track_id is None:

                continue


            byte_track_id = int(
                byte_track_id
            )


            # ------------------------------------------------
            # Bounding box
            # ------------------------------------------------

            bbox = (
                tracked.xyxy[index]
                .astype(float)
                .tolist()
            )


            # ------------------------------------------------
            # Confidence
            # ------------------------------------------------

            if tracked.confidence is not None:

                confidence = float(
                    tracked.confidence[index]
                )

            else:

                confidence = 0.0


            # ------------------------------------------------
            # Global ID
            # ------------------------------------------------

            global_id = get_global_id(
                source,
                class_name,
                byte_track_id
            )


            # ------------------------------------------------
            # Bottom-center position
            # ------------------------------------------------

            center_x, bottom_y = (
                get_bottom_center(bbox)
            )


            # =================================================
            # SPEED ESTIMATION
            # =================================================

            speed_estimate = None


            speed_key = (
                source,
                class_name,
                byte_track_id
            )


            previous_speed_data = (
                previous_speed_positions.get(
                    speed_key
                )
            )


            if is_vehicle(class_name):


                if previous_speed_data is not None:

                    previous_x = (
                        previous_speed_data[0]
                    )

                    previous_y = (
                        previous_speed_data[1]
                    )

                    previous_time = (
                        previous_speed_data[2]
                    )


                    current_time = (
                        timestamp_ms / 1000.0
                    )


                    delta_time = (
                        current_time
                        -
                        previous_time
                    )


                    if delta_time > 0:

                        distance_pixels = (
                            (
                                (
                                    center_x
                                    -
                                    previous_x
                                ) ** 2
                            )
                            +
                            (
                                (
                                    bottom_y
                                    -
                                    previous_y
                                ) ** 2
                            )
                        ) ** 0.5


                        speed_estimate = (
                            distance_pixels
                            /
                            delta_time
                        )


                        current_vehicle_speeds.append(
                            speed_estimate
                        )


                        all_speed_values.append(
                            speed_estimate
                        )


                # ------------------------------------------------
                # IMPORTANT:
                # Update previous position AFTER
                # calculating speed.
                # ------------------------------------------------

                previous_speed_positions[
                    speed_key
                ] = (
                    center_x,
                    bottom_y,
                    timestamp_ms / 1000.0
                )


            else:

                # Infrastructure / road damage
                # does not receive speed.

                speed_estimate = None


            # =================================================
            # ADD TRACKED OBJECT
            # =================================================

            tracked_object = {

                "tracking_id": global_id,

                "class_name": class_name,

                "confidence": confidence,

                "bbox": [
                    float(bbox[0]),
                    float(bbox[1]),
                    float(bbox[2]),
                    float(bbox[3]),
                ],

                "frame_id": frame_id,

                "speed_estimate": speed_estimate,

                "source": source,
            }


            tracked_objects.append(
                tracked_object
            )


    # ========================================================
    # VEHICLE COUNTING
    # ========================================================

    current_vehicle_count = 0


    for tracked_object in tracked_objects:


        class_name = (
            tracked_object["class_name"]
        )


        # Only vehicles are counted.

        if not is_vehicle(class_name):

            continue


        current_vehicle_count += 1


        global_id = (
            tracked_object["tracking_id"]
        )


        bbox = (
            tracked_object["bbox"]
        )


        _, current_bottom = (
            get_bottom_center(bbox)
        )


        # ----------------------------------------------------
        # Get previous bottom position
        # ----------------------------------------------------

        previous_bottom = (
            previous_count_positions.get(
                global_id
            )
        )


        # ----------------------------------------------------
        # Detect downward crossing
        # ----------------------------------------------------

        crossed_down = False

        if previous_bottom is not None:

            crossed_down = (

                previous_bottom
                <
                (
                    LINE_Y
                    -
                    COUNTING_MARGIN
                )

                and

                current_bottom
                >=
                (
                    LINE_Y
                    +
                    COUNTING_MARGIN
                )
            )


        # ----------------------------------------------------
        # Detect upward crossing
        # ----------------------------------------------------

        crossed_up = False

        if previous_bottom is not None:

            crossed_up = (

                previous_bottom
                >
                (
                    LINE_Y
                    +
                    COUNTING_MARGIN
                )

                and

                current_bottom
                <=
                (
                    LINE_Y
                    -
                    COUNTING_MARGIN
                )
            )


        # ----------------------------------------------------
        # Count vehicle ONCE
        # ----------------------------------------------------

        if (

            (crossed_down or crossed_up)

            and

            global_id
            not in
            counted_vehicle_ids

        ):


            counted_vehicle_ids.add(
                global_id
            )


            total_vehicle_count += 1


            if crossed_down:

                direction = "down"

            else:

                direction = "up"


            print(
                "\nVEHICLE COUNTED -> "
                f"ID={global_id}, "
                f"class={class_name}, "
                f"frame={frame_id}, "
                f"previous_bottom="
                f"{previous_bottom:.1f}, "
                f"current_bottom="
                f"{current_bottom:.1f}, "
                f"direction={direction}, "
                f"TOTAL="
                f"{total_vehicle_count}"
            )


        # ----------------------------------------------------
        # IMPORTANT:
        # Update counting position AFTER checking crossing.
        # ----------------------------------------------------

        previous_count_positions[
            global_id
        ] = current_bottom


    # ========================================================
    # FRAME AVERAGE SPEED
    # ========================================================

    if current_vehicle_speeds:

        frame_avg_speed = (

            sum(
                current_vehicle_speeds
            )

            /

            len(
                current_vehicle_speeds
            )
        )

    else:

        frame_avg_speed = 0.0


    # ========================================================
    # CONGESTION
    # ========================================================

    # Project rule:
    #
    # HIGH congestion:
    # high vehicle density
    # +
    # low speed
    # sustained for 3+ readings.
    #
    # Current prototype thresholds:
    #
    # current_vehicle_count >= 5
    # average speed <= 150 pixels/sec


    high_density = (
        current_vehicle_count >= 5
    )


    low_speed = (
        frame_avg_speed <= 150
    )


    if (
        high_density
        and
        low_speed
    ):

        congestion_streak += 1

    else:

        congestion_streak = 0


    if congestion_streak >= 3:

        congestion_level = "HIGH"

    elif (
        high_density
        and
        low_speed
    ):

        congestion_level = "MEDIUM"

    else:

        congestion_level = "LOW"


    # ========================================================
    # M3 FRAME OUTPUT
    # ========================================================

    m3_frame = {

        "frame_id": frame_id,

        "timestamp_ms": timestamp_ms,

        "tracked_objects": tracked_objects,

        "vehicle_count": total_vehicle_count,

        "current_vehicle_count":
            current_vehicle_count,

        "avg_speed": frame_avg_speed,

        "congestion_level":
            congestion_level,
    }


    # ========================================================
    # M5 FRAME OUTPUT
    # ========================================================

    m5_frame = {

        "frame_id": frame_id,

        "timestamp_ms": timestamp_ms,

        "timestamp": timestamp,

        "tracked_objects": tracked_objects,

        "vehicle_count": total_vehicle_count,

        "current_vehicle_count":
            current_vehicle_count,

        "avg_speed": frame_avg_speed,

        "congestion_level":
            congestion_level,
    }


    m3_frames.append(
        m3_frame
    )

    m5_frames.append(
        m5_frame
    )


    # ========================================================
    # TERMINAL PROGRESS
    # ========================================================

    if frame_id % 10 == 0:

        print(
            f"Frame {frame_id}: "
            f"vehicles="
            f"{current_vehicle_count}, "
            f"total_count="
            f"{total_vehicle_count}, "
            f"avg_speed="
            f"{frame_avg_speed:.4f}, "
            f"congestion="
            f"{congestion_level}"
        )


# ============================================================
# FINAL AVERAGE SPEED
# ============================================================

if all_speed_values:

    final_avg_speed = (

        sum(
            all_speed_values
        )

        /

        len(
            all_speed_values
        )
    )

else:

    final_avg_speed = 0.0


# ============================================================
# FINAL CONGESTION
# ============================================================

if m5_frames:

    final_congestion = (
        m5_frames[-1]
        ["congestion_level"]
    )

else:

    final_congestion = "LOW"


# ============================================================
# COMPLETE M3 OUTPUT
# ============================================================

m3_output = {

    "frames": m3_frames,

    "vehicle_count":
        total_vehicle_count,

    "avg_speed":
        final_avg_speed,

    "congestion_level":
        final_congestion,
}


# ============================================================
# COMPLETE M5 OUTPUT
# ============================================================

m5_output = {

    "frames": m5_frames,

    "vehicle_count":
        total_vehicle_count,

    "avg_speed":
        final_avg_speed,

    "congestion_level":
        final_congestion,
}


# ============================================================
# JSON SAFETY
# ============================================================

m3_output = make_json_safe(
    m3_output
)

m5_output = make_json_safe(
    m5_output
)


# ============================================================
# DELETE OLD OUTPUT FILES
# ============================================================

print("\n" + "=" * 70)
print("REMOVING OLD OUTPUT FILES")
print("=" * 70)


if M3_OUTPUT_FILE.exists():

    M3_OUTPUT_FILE.unlink()

    print(
        "Deleted:"
    )

    print(
        M3_OUTPUT_FILE
    )

else:

    print(
        "M3 output did not exist."
    )


if M5_OUTPUT_FILE.exists():

    M5_OUTPUT_FILE.unlink()

    print(
        "Deleted:"
    )

    print(
        M5_OUTPUT_FILE
    )

else:

    print(
        "M5 output did not exist."
    )


# ============================================================
# WRITE NEW M3 FILE
# ============================================================

with open(
    M3_OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        m3_output,
        file,
        indent=4,
        ensure_ascii=False
    )


# ============================================================
# WRITE NEW M5 FILE
# ============================================================

with open(
    M5_OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        m5_output,
        file,
        indent=4,
        ensure_ascii=False
    )


print("\n" + "=" * 70)
print("NEW OUTPUT FILES CREATED")
print("=" * 70)


print(
    f"\nM3 output saved to:"
)

print(
    M3_OUTPUT_FILE
)


print(
    f"\nM5 output saved to:"
)

print(
    M5_OUTPUT_FILE
)


# ============================================================
# VERIFY M3
# ============================================================

with open(
    M3_OUTPUT_FILE,
    "r",
    encoding="utf-8"
) as file:

    saved_m3 = json.load(
        file
    )


# ============================================================
# VERIFY M5
# ============================================================

with open(
    M5_OUTPUT_FILE,
    "r",
    encoding="utf-8"
) as file:

    saved_m5 = json.load(
        file
    )


# ============================================================
# OUTPUT VERIFICATION
# ============================================================

print("\n" + "=" * 70)
print("OUTPUT FILE VERIFICATION")
print("=" * 70)


print(
    f"\nM3 saved frames: "
    f"{len(saved_m3['frames'])}"
)


print(
    f"M3 saved vehicle count: "
    f"{saved_m3['vehicle_count']}"
)


print(
    f"M3 saved average speed: "
    f"{saved_m3['avg_speed']}"
)


print(
    f"M3 saved congestion: "
    f"{saved_m3['congestion_level']}"
)


print(
    f"\nM5 saved frames: "
    f"{len(saved_m5['frames'])}"
)


print(
    f"M5 saved vehicle count: "
    f"{saved_m5['vehicle_count']}"
)


print(
    f"M5 saved average speed: "
    f"{saved_m5['avg_speed']}"
)


print(
    f"M5 saved congestion: "
    f"{saved_m5['congestion_level']}"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("M1 -> M2 INTEGRATION COMPLETED SUCCESSFULLY")
print("=" * 70)


print(
    f"\nTOTAL UNIQUE VEHICLES COUNTED: "
    f"{total_vehicle_count}"
)


print(
    f"AVERAGE SPEED: "
    f"{final_avg_speed}"
)


print(
    f"FINAL CONGESTION: "
    f"{final_congestion}"
)


print(
    "\nM3 output:"
)

print(
    M3_OUTPUT_FILE
)


print(
    "\nM5 output:"
)

print(
    M5_OUTPUT_FILE
)


print("\n" + "=" * 70)