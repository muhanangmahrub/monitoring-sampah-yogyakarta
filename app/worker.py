import redis
import json
import onnxruntime as ort
import numpy as np
import psycopg2
import os
from app.utils import preprocessing, postprocessing
from dotenv import load_dotenv

load_dotenv()

session = ort.InferenceSession("./best.onnx")
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
conn = psycopg2.connect(
        host="localhost",
        database=os.getenv("INFERENCE_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASS_INFERENCE"),
    )

cursor = conn.cursor()

while True:
    _, task = redis_client.brpop('task_queue', timeout=0)
    task = json.loads(task)
    print(f"Processing task {task['task_id']} from camera {task['camera_id']}")
    frame = preprocessing.preprocess(task["frame"])
    inputs = {session.get_inputs()[0].name: frame["batch"]}
    outputs = session.run(None, inputs)
    outputs = [output.tolist() for output in outputs]
    arr = np.array(outputs[0])
    score, box, cls = postprocessing.postprocess(arr=arr, metadata=frame["metadata"])
    redis_client.hset(f'task_result:{task["task_id"]}', mapping={"result": json.dumps({
        "score": score.tolist(),
        "box": box.tolist(),
        "cls": cls.tolist()
    })})

    if len(box) == 0:
        continue
    cursor.execute(
        "INSERT INTO detections (camera_id, task_id, class, score, box) VALUES (%s, %s, %s, %s, %s)",
        (task["camera_id"], task["task_id"], "dirty" if cls[0] == 1 else "clean", float(score[0]), json.dumps(box.tolist()))
    )
    conn.commit()
