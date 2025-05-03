import cv2
import time
from ultralytics import YOLO

# Load YOLO OBB model
model = YOLO("best1.pt")  # Replace with your trained model

# Open webcam once at start
cap = cv2.VideoCapture(0)  # Change index if using a different camera
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce frame buffer latency
cap.set(cv2.CAP_PROP_FPS, 30)  # Adjust FPS based on hardware capability
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set resolution (optional)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

DRIP_FACTOR = 20  # Adjust based on IV set (e.g., 60 for microdrip, 15 or 20 for macrodrip)

def detect_drops():
    """ Detects IV drops using YOLO-OBB and calculates flow rate in mL/min """
    drop_count = 0
    prev_drop_detected = False
    consecutive_frames = 0
    last_drop_time = time.time()
    start_time = time.time()

    while time.time() - start_time < 60:  # Run for 1 minute
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Run YOLO inference
        results = model(frame, verbose=False)
        current_drop_detected = False

        for result in results:
            if not hasattr(result, 'obb') or result.obb is None:
                continue  # Skip if no OBB detections

            for det in result.obb:
                conf = det.conf.item()  # Get confidence score
                if conf < 0.8:
                    continue  # Ignore detections with low confidence

                current_drop_detected = True
                consecutive_frames += 1

                # Ensure drop is detected for at least 20 frames AND time gap > 0.5 sec
                current_time = time.time()
                if not prev_drop_detected and (current_time - last_drop_time) > 0.5 and consecutive_frames >= 20:
                    drop_count += 1
                    prev_drop_detected = True
                    last_drop_time = current_time

        # Reset consecutive frame count if no drop detected
        if not current_drop_detected:
            consecutive_frames = 0
            prev_drop_detected = False

    # Calculate Flow Rate
    flow_rate = drop_count / DRIP_FACTOR  # mL per minute
    print(f"Drops detected in 1 minute: {drop_count}")
    print(f"Calculated IV Flow Rate: {flow_rate:.2f} mL/min")

    return flow_rate

# Ensure camera is released on exit
if __name__ == "__main__":
    try:
        while True:
            flow_rate = detect_drops()
            print("Waiting for 5 minutes before the next cycle...")
            time.sleep(300)  # 5 minutes pause
    except KeyboardInterrupt:
        print("Stopping YOLO Detection...")
        cap.release()
        cv2.destroyAllWindows()
