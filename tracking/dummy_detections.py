# ============================================================
# DUMMY M1 OUTPUT FOR M2 TESTING
# ============================================================
#
# This follows the actual M1 detection format:
#
# class_id
# type
# source
# confidence
# frame_id
# timestamp_ms
# timestamp
# bbox
#
# M2 uses "type" as class_name.
# M2 ignores class_id.
# ============================================================


dummy_detections = [

    # ========================================================
    # FRAME 0
    # ========================================================

    {
        "class_id": 2,
        "type": "car",
        "source": "vehicle",
        "confidence": 0.92,
        "frame_id": 0,
        "timestamp_ms": 0,
        "timestamp": "2026-09-10T00:29:47.503023+05:30",
        "bbox": [100, 200, 140, 260]
    },

    {
        "class_id": 5,
        "type": "bus",
        "source": "vehicle",
        "confidence": 0.88,
        "frame_id": 0,
        "timestamp_ms": 0,
        "timestamp": "2026-09-10T00:29:47.503023+05:30",
        "bbox": [300, 200, 350, 270]
    },

    {
        "class_id": 9,
        "type": "stop_sign",
        "source": "infrastructure",
        "confidence": 0.91,
        "frame_id": 0,
        "timestamp_ms": 0,
        "timestamp": "2026-09-10T00:29:47.503023+05:30",
        "bbox": [500, 120, 550, 180]
    },


    # ========================================================
    # FRAME 1
    # ========================================================

    {
        "class_id": 2,
        "type": "car",
        "source": "vehicle",
        "confidence": 0.90,
        "frame_id": 1,
        "timestamp_ms": 100,
        "timestamp": "2026-09-10T00:29:47.603023+05:30",
        "bbox": [120, 200, 160, 260]
    },

    {
        "class_id": 5,
        "type": "bus",
        "source": "vehicle",
        "confidence": 0.87,
        "frame_id": 1,
        "timestamp_ms": 100,
        "timestamp": "2026-09-10T00:29:47.603023+05:30",
        "bbox": [280, 200, 330, 270]
    },

    {
        "class_id": 9,
        "type": "stop_sign",
        "source": "infrastructure",
        "confidence": 0.89,
        "frame_id": 1,
        "timestamp_ms": 100,
        "timestamp": "2026-09-10T00:29:47.603023+05:30",
        "bbox": [505, 120, 555, 180]
    },


    # ========================================================
    # FRAME 2
    # ========================================================

    {
        "class_id": 2,
        "type": "car",
        "source": "vehicle",
        "confidence": 0.91,
        "frame_id": 2,
        "timestamp_ms": 200,
        "timestamp": "2026-09-10T00:29:47.703023+05:30",
        "bbox": [140, 200, 180, 260]
    },

    {
        "class_id": 5,
        "type": "bus",
        "source": "vehicle",
        "confidence": 0.89,
        "frame_id": 2,
        "timestamp_ms": 200,
        "timestamp": "2026-09-10T00:29:47.703023+05:30",
        "bbox": [260, 200, 310, 270]
    },

    {
        "class_id": 9,
        "type": "stop_sign",
        "source": "infrastructure",
        "confidence": 0.92,
        "frame_id": 2,
        "timestamp_ms": 200,
        "timestamp": "2026-09-10T00:29:47.703023+05:30",
        "bbox": [510, 120, 560, 180]
    },


    # ========================================================
    # FRAME 3
    # ========================================================

    {
        "class_id": 2,
        "type": "car",
        "source": "vehicle",
        "confidence": 0.93,
        "frame_id": 3,
        "timestamp_ms": 300,
        "timestamp": "2026-09-10T00:29:47.803023+05:30",
        "bbox": [160, 200, 200, 260]
    },

    {
        "class_id": 5,
        "type": "bus",
        "source": "vehicle",
        "confidence": 0.90,
        "frame_id": 3,
        "timestamp_ms": 300,
        "timestamp": "2026-09-10T00:29:47.803023+05:30",
        "bbox": [240, 200, 290, 270]
    },

    {
        "class_id": 9,
        "type": "stop_sign",
        "source": "infrastructure",
        "confidence": 0.90,
        "frame_id": 3,
        "timestamp_ms": 300,
        "timestamp": "2026-09-10T00:29:47.803023+05:30",
        "bbox": [515, 120, 565, 180]
    },


    # ========================================================
    # FRAME 4
    # ========================================================

    {
        "class_id": 2,
        "type": "car",
        "source": "vehicle",
        "confidence": 0.92,
        "frame_id": 4,
        "timestamp_ms": 400,
        "timestamp": "2026-09-10T00:29:47.903023+05:30",
        "bbox": [180, 200, 220, 260]
    },

    {
        "class_id": 5,
        "type": "bus",
        "source": "vehicle",
        "confidence": 0.88,
        "frame_id": 4,
        "timestamp_ms": 400,
        "timestamp": "2026-09-10T00:29:47.903023+05:30",
        "bbox": [220, 200, 270, 270]
    },

    {
        "class_id": 9,
        "type": "stop_sign",
        "source": "infrastructure",
        "confidence": 0.91,
        "frame_id": 4,
        "timestamp_ms": 400,
        "timestamp": "2026-09-10T00:29:47.903023+05:30",
        "bbox": [520, 120, 570, 180]
    }
]