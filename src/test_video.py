from ultralytics import YOLO

model = YOLO("yolo26n.pt")

model.predict(
    source="videos/road.mp4",
    save=True,
    conf=0.4
)