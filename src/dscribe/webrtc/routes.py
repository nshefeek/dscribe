import json
import asyncio
from logging import getLogger

from fastapi import APIRouter, WebSocket
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate


logger = getLogger(__name__)

webrtc_router = APIRouter(
    prefix="/ws",
    tags=["WebRTC routes"],
    responses={404: {"description": "Not found"}},
)

pcs = set()


@webrtc_router.websocket("")
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
            message = await websocket.receive_text()
            data = json.loads(message)
            print(f"{data}")

            if data["type"] == "offer":
                offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                await pc.setRemoteDescription(offer)
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                await websocket.send_json({
                    "type": "answer",
                    "sdp": pc.localDescription.sdp,
                })
            elif data["type"] == "ice-candidate":
                candidate = data["candidate"]
                candidate_parts = candidate["candidate"].split()
                if candidate_parts:
                    # import pdb; pdb.set_trace()
                    candidate = RTCIceCandidate(
                        foundation=candidate_parts[0],
                        component=int(candidate_parts[1]),
                        protocol=candidate_parts[2].lower(),
                        priority=int(candidate_parts[3]),
                        ip=candidate_parts[4],
                        port=int(candidate_parts[5]),
                        type=candidate_parts[7],
                        sdpMid=candidate["sdpMid"],
                        sdpMLineIndex=candidate["sdpMLineIndex"]
                    )
                    await pc.addIceCandidate(candidate)
                else:
                    continue
    finally:
        await pc.close()
        pcs.discard(pc)


async def close_peer_connections():
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()