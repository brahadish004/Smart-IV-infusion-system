from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import time
import threading

factory = PiGPIOFactory()
servo = Servo(17, pin_factory=factory)

running = False
paused = True
direction = 1
current_value = -1  # Start at one end
servo_thread = None

# Create all step values once
step_values = [-1 + (i * (2 / 11)) for i in range(12)]

def run_servo():
    global current_value, running, paused
    while running:
        if not paused:
            # Find nearest index to current_value
            try:
                index = min(range(len(step_values)), key=lambda i: abs(step_values[i] - current_value))
            except:
                index = 0

            # Build the sequence starting from that index
            if direction == 1:
                step_sequence = step_values[index:]
            else:
                step_sequence = reversed(step_values[:index+1])

            for value in step_sequence:
                if paused or not running:
                    break
                servo.value = value
                current_value = value
                time.sleep(0.5)  # Adjust speed as needed
        else:
            time.sleep(0.1)

def continue_servo():
    global paused, running, servo_thread
    paused = False
    if not running:
        running = True
        servo_thread = threading.Thread(target=run_servo, daemon=True)
        servo_thread.start()
    print("Command: CONTINUE")

def pause_servo():
    global paused
    paused = True
    print("Command: PAUSE")

def stop_servo():
    global running, paused, current_value
    running = False
    paused = True
    servo.value = 1  # neutral or stopped position
    # Don't keep this as current_value, or it will resume from wrong position
    current_value = 1  # or nearest valid in your sweep range (e.g., step_values[0] or step_values[-1])
    print("Command: STOP")

def reset_servo():
    global running, paused, current_value
    running = False
    paused = True
    servo.value = -1
    current_value = -1  # properly update this too
    print("Command: RESET")

def set_direction(new_direction):
    global direction
    direction = -1 if new_direction == 1 else 1
    print(f"Direction set to: {'REVERSE' if direction == -1 else 'FORWARD'}")
