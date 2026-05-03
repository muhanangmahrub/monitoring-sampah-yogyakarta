import cv2
import base64
import requests
import time
import json

# cap = cv2.VideoCapture("/Users/muhamadanangmahrub/Downloads/ML Project/monitoring sampah yogyakarta/video_testing.mp4")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Cant't receive frame (stream end). Exiting ...")
        break
    _, buffer = cv2.imencode('.jpg', frame)
    b64_string = base64.b64encode(buffer).decode('utf-8')
    response = requests.post('http://localhost:8000/tasks', json={"frames": [b64_string], "camera_id": 1})
    task_ids = response.json()["task_ids"]
    if len(task_ids) == 0:
        continue
    task_id = task_ids[0]
    while True:
        response = requests.get(f'http://localhost:8000/tasks/{task_id}')
        if response.json()["status"] == "completed":
            break
        time.sleep(0.033)
    result = response.json()["result"]
    result = json.loads(result['result'])
    if len(result["box"]) == 0:
        continue
    box = result["box"][0]
    cls = "dirty" if result["cls"][0] == 1 else "clean"
    score = result["score"]
    cv2.rectangle(frame, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
    cv2.putText(frame, f'{cls}: {score[0]:.2f}', (int(box[2]), int(box[3]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow('Camera', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()