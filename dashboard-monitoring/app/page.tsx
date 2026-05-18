"use client";

import { useEffect, useState } from "react";

interface Detection {
  camera_id: number;
  detection_id: number;
  class: string;
  score: number;
  box: [number, number, number, number];
  timestamp: string;
  streakStart: string;
  latency_ms: number;
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
      setData((prev) => {
        return data.tasks.reduce(
          (acc: { [key: number]: Detection }, item: Detection) => {
            const prevCamera = prev?.[item.camera_id];
            const streakStart =
              prevCamera && prevCamera.class === item.class
                ? prevCamera.streakStart
                : item.timestamp;
            acc[item.camera_id] = { ...item, streakStart };
            return acc;
          },
          { ...prev },
        );
      });
    };

    return () => {
      ws.close();
      console.log("WebSocket connection closed");
    };
  }, []);

  return (
    <div className="bg-gray-100 min-h-screen p-5">
      <h1 className="text-2xl/7 font-bold text-gray-800 sm:truncate sm:text-3xl sm:tracking-tight">
        Dashboard Monitoring
      </h1>
      {data ? (
        <div className="grid grid-cols-3 gap-5">
          {Object.values(data).map((item) => (
            <div
              key={item.camera_id}
              className="max-w-sm rounded overflow-hidden shadow-lg p-4 bg-white"
            >
              <div className="px-6 py-4">
                <h2 className="text-gray-700 text-base">
                  Camera ID: {item.camera_id}
                </h2>
                <p className="text-gray-600">
                  Detection ID: {item.detection_id}
                </p>
                <span
                  className={
                    item.class === "dirty"
                      ? "bg-red-500 text-white px-2 py-1 rounded"
                      : "bg-green-500 text-white px-2 py-1 rounded"
                  }
                >
                  Class: {item.class}
                </span>
                <p className="text-gray-600">Score: {item.score.toFixed(2)}</p>
                {/* <p className="text-gray-600">Box: {item.box.join(", ")}</p> */}
                <p className="text-gray-600">Timestamp: {item.timestamp}</p>
                <p className="text-gray-600">
                  Streak Start: {item.streakStart}
                </p>
                <p className="text-gray-600">Latency: {item.latency_ms}ms</p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p>Loading data...</p>
      )}
    </div>
  );
}
