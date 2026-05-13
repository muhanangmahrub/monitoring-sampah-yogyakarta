"use client";

import { useEffect, useState } from "react";

interface Detection {
  camera_id: number;
  detection_id: number;
  class: number;
  score: number;
  box: [number, number, number, number];
  timestamp: string;
}

export default function Dashboard() {
  const [data, setData] = useState<{ [key: number]: Detection } | null>(null);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => {
      console.log("WebSocket connection established");
      ws.send(JSON.stringify({ last_id: 0 }));
    };
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const cameras = data.tasks.reduce(
        (acc: { [key: number]: Detection }, item: Detection) => {
          acc[item.camera_id] = item;
          return acc;
        },
        {},
      );
      setData(cameras);
    };

    return () => {
      ws.close();
      console.log("WebSocket connection closed");
    };
  }, []);

  return (
    <div>
      <h1>Dashboard Monitoring</h1>
      {data ? (
        <pre>{JSON.stringify(data, null, 2)}</pre>
      ) : (
        <p>Loading data...</p>
      )}
    </div>
  );
}
