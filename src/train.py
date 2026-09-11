from pathlib import Path
from ultralytics import YOLO


def main():
    project_root = Path(__file__).resolve().parent.parent
    data_yaml = project_root / "data" / "data.yaml"

    print(f"Using dataset: {data_yaml}")
    print(f"Dataset exists: {data_yaml.exists()}")

    # Start fresh from pretrained YOLO11n
    model = YOLO("yolo11n.pt")

    model.train(
        data=str(data_yaml),
        epochs=50,
        imgsz=640,
        batch=16,
        device="mps",
        name="infrastructure_model_new"
    )


if __name__ == "__main__":
    main()