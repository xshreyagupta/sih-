from ultralytics import YOLO

def train_infrastructure_model():
    model = YOLO("yolov8n.pt")

    model.train(
        data="../data/infrastructure/data.yaml",
        epochs=30,
        imgsz=640,
        batch=4,
        workers=2,
        device="mps",
        project="../runs/detect",
        name="infrastructure_model",
        exist_ok=True
    )

if __name__ == "__main__":
    train_infrastructure_model()