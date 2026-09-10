from ultralytics import YOLO

def run_full_training():
    model = YOLO("../yolo26n.pt")

    print("Starting optimized road defect training on Apple M2...")

    model.train(
        data="../data/pothole/India/data.yaml",
        epochs=50,
        imgsz=640,
        batch=4,             # REDUCED: Prevents RAM overflow & SSD swapping
        workers=2,           # ADDED: Optimizes CPU data loading on Mac
        device="mps",
        project="../runs/detect",
        name="india_test",
        exist_ok=True,
        perspective=0.0005,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        mosaic=1.0
    )

if __name__ == "__main__":
    run_full_training()
       