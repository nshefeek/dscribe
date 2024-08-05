import asyncio

from fastapi import FastAPI, WebSocket
from aiortc import RTCPeerConnection, RTCSessionDescription


webrtc_app = FastAPI()

pcs = set()


@webrtc_app.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        if  pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    try:
        while True:
            message = await websocket.receive_json()
            if message["type"] == "offer":
                offer = RTCSessionDescription(sdp=message["sdp"], type=message["type"])
                await pc.setRemoteDescription(offer)
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                await websocket.send_json({
                    "type": "answer",
                    "sdp": pc.localDescription.sdp,
                })
            elif message["type"] == "ice-candidate":
                await pc.addIceCandidate(message["candidate"])
    finally:
        await pc.close()
        pcs.discard(pc)


async def close_peer_connections():
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()