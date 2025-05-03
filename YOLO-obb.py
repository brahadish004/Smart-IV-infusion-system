from ultralytics import YOLO

# Load a pretrained YOLOv8 OBB model
model = YOLO('yolov8n-obb.pt')

# Train the model
model.train(data="E:\iv drip 2.o.v2i.yolov8-obb new\data.yaml",epochs=50,          # Number of training epochs
    batch=2,            # Reduce batch size for better CPU performance
    imgsz=640,          # Set image size to 640
    device="cpu",       # Force CPU usage
    workers=0  )
