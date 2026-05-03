CREATE TABLE IF NOT EXISTS detections (
    detection_id SERIAL PRIMARY KEY,
    camera_id INT NOT NULL,
    task_id UUID NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    class VARCHAR(20) NOT NULL,
    score FLOAT NOT NULL,
    box JSONB NOT NULL,
    FOREIGN KEY (camera_id) REFERENCES cameras(camera_id)
);