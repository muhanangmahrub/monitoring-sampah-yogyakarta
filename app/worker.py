import redis
import json
import onnxruntime as ort
from app.utils import preprocessing

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
    inputs = {session.get_inputs()[0].name: frame}
    outputs = session.run(None, inputs)
    outputs = [output.tolist() for output in outputs]
    # Push result back to redis with task_id
    redis_client.hset(f'task_result:{task["task_id"]}', mapping={"result": json.dumps(outputs)})
