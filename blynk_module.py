import BlynkLib
import time
import threading
from ultra_module import get_ml_level
from yolo_module import detect_drops
from servo_module import stop_servo, continue_servo, reset_servo, set_direction, pause_servo

# Blynk Auth and Server Details
BLYNK_AUTH = "z2fxgQYIubou_LQtRo6plx3uzNm8jzAi"
BLYNK_SERVER = "blr1.blynk.cloud"
BLYNK_PORT = 8080

blynk = BlynkLib.Blynk(BLYNK_AUTH, server=BLYNK_SERVER, port=BLYNK_PORT)

# Virtual Pins
V_BOTTLE_CAPACITY = 7
V_IV_LEVEL = 5
V_FLOW_RATE = 8
V_PREDICTED_TIME = 6
V_DIRECTION = 0
V_PAUSE = 2
V_CONTINUE = 3
V_STOP = 1
V_RESET = 4

bottle_capacity = None
last_ultrasonic_time = 0
last_yolo_time = 0
ml_level = None
yolo_thread_running = False

# --- Blynk Input Handlers ---
@blynk.VIRTUAL_WRITE(V_BOTTLE_CAPACITY)
def set_bottle_capacity(value):
    global bottle_capacity
    try:
        bottle_capacity = int(value[0])
        print(f"[BLYNK] Bottle Capacity Set: {bottle_capacity} mL")
    except ValueError:
        print("[ERROR] Invalid input for bottle capacity")

@blynk.VIRTUAL_WRITE(V_DIRECTION)
def direction_command(value):
    set_direction(int(value[0]))

@blynk.VIRTUAL_WRITE(V_PAUSE)
def pause_command(value):
    if int(value[0]) == 1:
        pause_servo()

@blynk.VIRTUAL_WRITE(V_CONTINUE)
def continue_command(value):
    if int(value[0]) == 1:
        continue_servo()

@blynk.VIRTUAL_WRITE(V_STOP)
def stop_command(value):
    if int(value[0]) == 1:
        stop_servo()

@blynk.VIRTUAL_WRITE(V_RESET)
def reset_command(value):
    if int(value[0]) == 1:
        reset_servo()

# --- Utility ---
def get_predicted_emptying_time(volume_ml, flow_rate):
    if flow_rate <= 0:
        return 0
    return round(volume_ml / flow_rate, 2)

# --- YOLO Worker Thread ---
def run_yolo_detection():
    global yolo_thread_running
    yolo_thread_running = True
    try:
        print("[YOLO] Starting 1-minute drop detection...")
        flow_rate = detect_drops()
        print("[YOLO] Drop detection completed.")

        if flow_rate is not None:
            blynk.virtual_write(V_FLOW_RATE, flow_rate)
            print(f"[YOLO] Flow Rate: {flow_rate:.2f} mL/min")

            if ml_level is not None and bottle_capacity and flow_rate > 0:
                predicted_time = get_predicted_emptying_time(ml_level, flow_rate)
                blynk.virtual_write(V_PREDICTED_TIME, predicted_time)
                print(f"[YOLO] Predicted Time Until Empty: {predicted_time} min")
            else:
                blynk.virtual_write(V_PREDICTED_TIME, 0)
                print("[WARN] Insufficient data for prediction.")
        else:
            print("[ERROR] YOLO detection failed.")
    except Exception as e:
        print(f"[ERROR] YOLO thread crashed: {e}")
    finally:
        yolo_thread_running = False

# --- Main Loop ---
while True:
    blynk.run()

    # Every 10s: Ultrasonic check
    if time.time() - last_ultrasonic_time >= 10:
        last_ultrasonic_time = time.time()

        ml_level = get_ml_level()
        if ml_level is not None and bottle_capacity:
            iv_percentage = max(0, min(100, (100 * ml_level) / bottle_capacity))
            blynk.virtual_write(V_IV_LEVEL, iv_percentage)
            print(f"[ULTRA] IV Level: {iv_percentage:.1f}%, Volume: {ml_level} mL")

            if iv_percentage == 0:
                stop_servo()
        else:
            print("[ERROR] Failed to read IV level or bottle capacity not set.")

    # Every 60s: YOLO detection in thread
    if time.time() - last_yolo_time >= 60 and not yolo_thread_running:
        last_yolo_time = time.time()
        threading.Thread(target=run_yolo_detection, daemon=True).start()

    time.sleep(1)
