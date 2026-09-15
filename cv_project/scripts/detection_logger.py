import cv2
import numpy as np
import csv
import time
from datetime import datetime
from picamera2 import Picamera2

try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    from tensorflow.lite.python.interpreter import Interpreter

MODEL_PATH = '/home/lhsengr06/cv_project/models/detect.tflite'
LABEL_PATH = '/home/lhsengr06/cv_project/models/labelmap.txt'
LOG_PATH = '/home/lhsengr06/cv_project/data/detections.csv'

CONFIDENCE_THRESHOLD = 0.5
TARGET_CLASSES = ['bird', 'cat', 'dog']
COOLDOWN_SECONDS = 5

with open(LABEL_PATH, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

interpreter = Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

input_height = input_details[0]['shape'][1]
input_width = input_details[0]['shape'][2]

try:
    with open(LOG_PATH, 'x', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'label', 'confidence'])
except FileExistsError:
    pass

last_logged = {}

picam2 = Picamera2()

picam2.configure(
    picam2.create_preview_configuration(
        main={"format": 'XRGB8888', "size": (640, 480)}
    )
)

picam2.start()

try:
    while True:
        frame = picam2.capture_array()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        frame_h, frame_w, _ = frame.shape

        resized = cv2.resize(
            frame,
            (input_width, input_height)
        )

        input_data = np.expand_dims(resized, axis=0)

        interpreter.set_tensor(
            input_details[0]['index'],
            input_data
        )

        interpreter.invoke()

        boxes = interpreter.get_tensor(
            output_details[0]['index']
        )[0]

        classes = interpreter.get_tensor(
            output_details[1]['index']
        )[0]

        scores = interpreter.get_tensor(
            output_details[2]['index']
        )[0]

        for i in range(len(scores)):

            if scores[i] < CONFIDENCE_THRESHOLD:
                continue

            class_id = int(classes[i])

            label = (
                labels[class_id]
                if class_id < len(labels)
                else "Unknown"
            )

            if label not in TARGET_CLASSES:
                continue

            ymin, xmin, ymax, xmax = boxes[i]

            x1 = int(xmin * frame_w)
            y1 = int(ymin * frame_h)
            x2 = int(xmax * frame_w)
            y2 = int(ymax * frame_h)

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"{label}: {scores[i]:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            now = time.time()

            if (
                label not in last_logged
                or (now - last_logged[label]) > COOLDOWN_SECONDS
            ):
                last_logged[label] = now

                timestamp = datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S'
                )

                with open(LOG_PATH, 'a', newline='') as f:
                    writer = csv.writer(f)

                    writer.writerow([
                        timestamp,
                        label,
                        f"{scores[i]:.2f}"
                    ])

                print(
                    f"Logged: {timestamp} - "
                    f"{label} ({scores[i]:.2f})"
                )

        cv2.imshow('Detection Logger', frame)

        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrupted by user")

finally:
    picam2.stop()
    cv2.destroyAllWindows()
