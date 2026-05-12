import redis
import uuid
import json
import asyncio
import psycopg2
import os
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor

load_dotenv()

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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    conn = psycopg2.connect(
        host="localhost",
        database=os.getenv("INFERENCE_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASS_INFERENCE"),
    )
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    data = await websocket.receive_text()
    last_id = json.loads(data).get("last_id", None)
    try:
        while True:
            if last_id:
                cursor.execute("SELECT * FROM detections WHERE detection_id > %s", (last_id,))
                new_tasks = cursor.fetchall()
            else:
                cursor.execute("SELECT * FROM detections")
                new_tasks = cursor.fetchall()
            if new_tasks:
                new_tasks = [dict(task) for task in new_tasks]
                new_tasks = [{**dict(task), "timestamp": task["timestamp"].strftime("%Y-%m-%d %H:%M:%S")} for task in new_tasks]
                await websocket.send_json({"tasks": new_tasks})
                last_id = new_tasks[-1]["detection_id"]
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        cursor.close()
        conn.close()