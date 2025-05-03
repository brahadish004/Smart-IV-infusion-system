import pigpio
from time import sleep, time

# Ultrasonic sensor pins
TRIG = 23
ECHO = 24

pi = pigpio.pi()
if not pi.connected:
    raise IOError("Could not connect to pigpio daemon")

pi.set_mode(TRIG, pigpio.OUTPUT)
pi.set_mode(ECHO, pigpio.INPUT)
pi.write(TRIG, 0)

# Distance-to-mL mapping
distance_map = {
    (1.0, 4.0): 500,
    (4.0, 4.8): 450,
    (4.8, 5.3): 400,
    (5.3, 6.6): 350,
    (6.6, 7.6): 300,
    (7.6, 8.6): 250,
    (8.6, 9.6): 200,
    (9.6, 10.9): 150,
    (10.9, 12.0): 100,
    (12.0, 15.0): 50,
    (15.0, 16.5): 0
}


def measure_distance(retries=3):
    """Measure distance using ultrasonic sensor with retry mechanism"""
    for _ in range(retries):
        pi.write(TRIG, 1)
        sleep(0.00001)
        pi.write(TRIG, 0)

        start_time = time()
        stop_time = start_time  # Ensure stop_time is always defined
        timeout = start_time + 0.3  # 50ms timeout

        while pi.read(ECHO) == 0 and time() < timeout:
            start_time = time()

        while pi.read(ECHO) == 1 and time() < timeout:
            stop_time = time()

        if time() >= timeout:
            print("Ultrasonic timeout. Retrying...")
            continue  # Retry reading

        distance = ((stop_time - start_time) * 34300) / 2
        return round(distance, 2)

    print("Failed to measure distance after retries.")
    return None  # Return None if all retries fail

def get_ml_level():
    """Return only the mL level based on distance, without percentage calculation"""
    distance = measure_distance()
    if distance is None:
        print("Ultrasonic timeout or read failure.")
        return None

    ml_level = None
    for (min_d, max_d), ml in distance_map.items():
        if min_d <= distance <= max_d:
            ml_level = ml
            break

    if ml_level is None:
        print("Distance out of range.")
    
    return ml_level
