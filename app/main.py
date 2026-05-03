import redis
import uuid
import json
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

class FrameList(BaseModel):
    frames: list[str]
    camera_id: int

@app.get("/")
async def root():
    return {"message": "API Monitoring Sampah Yogyakarta"}

@app.post('/tasks')
async def create_task(frame_list: FrameList):
    task_ids = []
    for frame in frame_list.frames:
        if redis_client.llen("task_queue") > 5:
            pass
        else:
            task_ids.append(str(uuid.uuid4()))
            redis_client.rpush('task_queue', json.dumps({"frame": frame, "task_id": task_ids[-1], "camera_id": frame_list.camera_id}))
    return {"task_ids": task_ids, "status": "queued"}


@app.get('/tasks/{task_id}')
async def get_task_result(task_id: str):
    results = redis_client.hgetall(f'task_result:{task_id}')
    if not results:
        return {"task_id": task_id, "status": "processing"}
    return {"task_id": task_id, "status": "completed", "result": results}