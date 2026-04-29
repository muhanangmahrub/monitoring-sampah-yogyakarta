import redis
import json
import onnxruntime as ort
import numpy as np
from app.utils import preprocessing, postprocessing

session = ort.InferenceSession("./best.onnx")
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


while True:
    # BRPOP from redis queue -> get {frame, task_id}
    _, task = redis_client.brpop('task_queue', timeout=0)
    print(f"Received task: {task[:50]}...")
    # json.loads to deserialize
    task = json.loads(task)
    # preprocess(frame) -> numpy array
    frame = preprocessing.preprocess(task["frame"])
    # ONNX inference
    inputs = {session.get_inputs()[0].name: frame["batch"]}
    outputs = session.run(None, inputs)
    outputs = [output.tolist() for output in outputs]
    arr = np.array(outputs[0])
    score, box, cls = postprocessing.postprocess(arr=arr, metadata=frame["metadata"])
    # Push result back to redis with task_id
    redis_client.hset(f'task_result:{task["task_id"]}', mapping={"result": json.dumps({
        "score": score.tolist(),
        "box": box.tolist(),
        "cls": cls.tolist()
    })})
