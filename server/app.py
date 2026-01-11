from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
from datetime import datetime
import os

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, sender: WebSocket = None):
        for connection in self.active_connections:
            if connection != sender:
                await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            # Broadcast to all connected clients
            # timestamp = datetime.now().strftime("%H:%M:%S")
            # message = f"[{timestamp}] {user_id}: {data}"
            message = f"{data}"
            await manager.broadcast(message, sender=websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"they left the chat")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)