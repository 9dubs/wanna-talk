import asyncio
import websockets
import sys
import aioconsole
from datetime import datetime

class UserExit(Exception):
    pass

async def receive_messages(websocket):
    """Continuously listen for incoming messages"""
    try:
        async for message in websocket:
            leave = False
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg = f"[{timestamp}] Them: {message}"
            if 'left' in message:
                msg = "they have left"  
            print(f"\r\033[K{msg}")  # \033[K clears line
            print(f"[{timestamp}] You: ", end="", flush=True)
    except websockets.exceptions.ConnectionClosed:
        print("\nConnection closed")

async def send_messages(websocket):
    """Read from terminal asynchronously"""
    try:
        while True:
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = await aioconsole.ainput(f"[{timestamp}] You: ")
            if message.lower() == 'quit':
                raise UserExit("You left...")
            if message.strip():
                await websocket.send(message)
    except KeyboardInterrupt:
        raise UserExit

async def chat(user_id):
    uri = f"ws://127.0.0.1:8000/ws/{user_id}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected as {user_id}. Type 'quit' to exit.\n")
            
            await asyncio.gather(
                receive_messages(websocket),
                send_messages(websocket),
                # return_exceptions=True
            )
    
    except UserExit:
        print(f"You left")
                
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    user_id = sys.argv[1] if len(sys.argv) > 1 else input("Enter your name: ")
    asyncio.run(chat(user_id))