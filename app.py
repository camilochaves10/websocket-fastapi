from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
import asyncio
from datetime import datetime, timezone

async def echo_message(websocket:WebSocket):
    data = await websocket.receive_text()
    await websocket.send_text(f'Message text was: {data}')

async def send_time(websocket: WebSocket):
    await asyncio.sleep(10)
    await websocket.send_text(f'It is: {datetime.utcnow().isoformat()}')



app = FastAPI()
@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept() #call method accept first to tell client we agree to open tunnel
    try: #necessary to handle client disconnection to use try-except block
        while True:
            echo_message_task = asyncio.create_task(echo_message(websocket)) #create_task transforms corroutine into task object
            send_time_task = asyncio.create_task(send_time(websocket))
            done, pending = await asyncio.wait(
                {echo_message_task, send_time_task},
                return_when = asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            for task in done:
                task.result()

    except WebSocketDisconnect:
        await websocket.close()
