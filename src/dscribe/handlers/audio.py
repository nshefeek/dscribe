
from typing import Coroutine, Any

from av import AudioFrame
from aiortc import MediaStreamTrack
from av.frame import Frame
from av.packet import Packet


class AudioProcessor(MediaStreamTrack):
    kind = "audio"

    def __init__(self, track) -> None:
        super().__init__()
        self.track = track

    async def recv(self) -> Coroutine[Any, Any, Frame | Packet]:
        frame = await self.track.recv()
        return self.process_audio(frame)
    
    def process_audio(self, frame: AudioFrame) -> AudioFrame:
        # Implement your audio processing logic here
        return frame