import React, {useState, useEffect, useCallback, useRef} from "react";

const WS_URL = "ws://localhost:8000/ws"
// const API_URL = "http://localhost:8000/api/v1"

const App: React.FC = () => {
  const [streaming, setStreaming] = useState(false);
  const [audioDevices, setAudioDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string>("");
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    async function getAudiDevices() {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const audioInputs = devices.filter(device => device.kind === "audioinput");
      setAudioDevices(audioInputs);
      if (audioInputs.length > 0) {
        setSelectedDeviceId(audioInputs[0].deviceId);
      }
    }
    getAudiDevices();

    wsRef.current = new WebSocket(WS_URL);
    wsRef.current.onmessage = handleWebSocketMessage;
  
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleWebSocketMessage = useCallback(async (event: MessageEvent) => {
    const message = JSON.parse(event.data);
    if (message.type == "answer") {
      const remoteDesc = new RTCSessionDescription(message);
      await peerConnectionRef.current?.setRemoteDescription(remoteDesc);
    } else if (message.type == "ice-candidate") {
      await peerConnectionRef.current?.addIceCandidate(message.candidate);
    }
  }, []);

  const startStreaming = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { deviceId: selectedDeviceId ? { exact: selectedDeviceId } : undefined }
      });
      streamRef.current = stream;

      const pc = new RTCPeerConnection();
      peerConnectionRef.current = pc;

      stream.getAudioTracks().forEach(track => {
        pc.addTrack(track, stream);
      });

      pc.onicecandidate = (event) => {
        if (event.candidate) {
          wsRef.current?.send(JSON. stringify({
            type: "ice-candidate",
            candidate: event.candidate
          }));
        }
      };

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      wsRef.current?.send(JSON.stringify({
        type: "offer",
        sdp: pc.localDescription?.sdp
      }));

    setStreaming(true);
  } catch (err) {
    console.error("Error starting stream:", err);
  }
  }, [selectedDeviceId]);

  const stopStreaming = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }
    setStreaming(false);
  }, []);
  
  return (
    <div>
      <select value={selectedDeviceId} onChange={(e) => setSelectedDeviceId(e.target.value)} disabled={streaming}>
        {audioDevices.map(device => (
          <option key={device.deviceId} value={device.deviceId}>
            {device.label || `Microphone ${device.deviceId.slice(0, 5)}`}
          </option>
        ))}
      </select>
      {!streaming ? (
        <button onClick={startStreaming} disabled={!selectedDeviceId}>Start Streaming</button>
      ): (
        <button onClick={stopStreaming}>Stop Streaming</button>
      )}
    </div>
  );
};

export default App;