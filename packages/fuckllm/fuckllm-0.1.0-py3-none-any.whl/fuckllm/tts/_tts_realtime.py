import asyncio
import json
import logging
import os
import time
import wave
from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, Any, Literal
import pyaudio
import websockets
import base64


SessionMode=Literal["server_commit", "commit"]
AudioFormat = Literal["pcm", "wav", "mp3"]
LanguageType = Literal["Auto", "Chinese", "English", "Japanese", "Korean", "Spanish", "French", "German"]


@dataclass
class AudioConfig:
    sample_rate: int = 24000
    channels: int = 1
    sample_width: int = 2
    chunk_size: int = 1024


@dataclass
class TTSConfig:
    base_url: str = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime?model=qwen3-tts-flash-realtime"
    api_key: Optional[str] = None
    mode: SessionMode = "server_commit"
    voice: str = "Cherry"
    language_type: LanguageType = "Auto"
    response_format: AudioFormat = "pcm"
    sample_rate: int = 24000

    def todict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "voice": self.voice,
            "language_type": self.language_type,
            "response_format": self.response_format,
            "sample_rate": self.sample_rate
        }

    @property
    def session_config(self) -> Dict[str, Any]:
        return self.todict()

    @classmethod
    def from_env(cls) -> 'TTSConfig':
        return cls(
            api_key=os.getenv("ali_api_key")
        )


class AudioManager:
    def __init__(self, config: AudioConfig = None):
        self.config = config or AudioConfig()
        self._audio_chunks: list[bytes] = []
        self._pyaudio = pyaudio.PyAudio()
        self._stream: Optional[pyaudio.Stream] = None

    def start_stream(self) -> None:
        if self._stream is None:
            self._stream = self._pyaudio.open(
                format=pyaudio.paInt16,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                output=True,
                frames_per_buffer=self.config.chunk_size
            )
            logging.info("audio stream started")

    def stop_stream(self) -> None:
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
            logging.info("audio stream stopped")

    def play_audio(self, audio_bytes: bytes) -> None:
        if self._stream:
            try:
                self._stream.write(audio_bytes)
                self._audio_chunks.append(audio_bytes)
                logging.debug(f"play audio block: {len(audio_bytes)} bytes")
            except Exception as e:
                logging.error(f"audio play failed: {e}")

    def save_to_file(self, filename: str) -> bool:
        if not self._audio_chunks:
            logging.warning("no audio data to save")
            return False

        try:
            audio_data = b"".join(self._audio_chunks)
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(self.config.channels)
                wav_file.setsampwidth(self.config.sample_width)
                wav_file.setframerate(self.config.sample_rate)
                wav_file.writeframes(audio_data)
            logging.info(f"audio saved to: {filename}")
            return True
        except Exception as e:
            logging.error(f"save audio failed: {e}")
            return False

    def cleanup(self) -> None:
        self.stop_stream()
        self._pyaudio.terminate()
        logging.info("audio manager cleaned")

@dataclass
class TTSRealtimeClient:
    config: TTSConfig
    audio_callback: Optional[Callable[[bytes], None]] = None
    ws: Optional[websockets.WebSocketServerProtocol] = None
    _current_response_id: Optional[str] = None
    _current_item_id: Optional[str] = None
    _is_responding: bool = False


    async def connect(self) -> None:
        if not self.config.api_key:
            raise ValueError("api key is not set")

        try:
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            self.ws = await websockets.connect(self.config.base_url, additional_headers=headers)

            await self.update_session(self.config.todict())
            logging.info("TTS service connected successfully")
        except Exception as e:
            logging.error(f"connection failed: {e}")
            raise

    async def send_event(self, event: Dict[str, Any]) -> None:
        if not self.ws:
            raise RuntimeError("WebSocket not connected")

        event['event_id'] = f"event_{int(time.time() * 1000)}"
        logging.debug(f"send event: type={event['type']}, event_id={event['event_id']}")
        await self.ws.send(json.dumps(event))


    async def update_session(self, session_dict: Dict[str, Any]) -> None:
        event = {
            "type": "session.update",
            "session": session_dict
        }
        logging.debug(f"update session config: {session_dict}")
        await self.send_event(event)

    async def append_text(self, text: str) -> None:
        event = {
            "type": "input_text_buffer.append",
            "text": text
        }
        await self.send_event(event)

    async def commit_text_buffer(self) -> None:
        event = {"type": "input_text_buffer.commit"}
        await self.send_event(event)

    async def clear_text_buffer(self) -> None:
        event = {"type": "input_text_buffer.clear"}
        await self.send_event(event)

    async def finish_session(self) -> None:
        event = {"type": "session.finish"}
        await self.send_event(event)


    async def handle_messages(self) -> None:        
        if not self.ws:
            raise RuntimeError("WebSocket not connected")

        try:
            async for message in self.ws:
                event = json.loads(message)
                event_type = event.get("type")

                if event_type not in ["response.audio.delta"]:
                    logging.debug(f"receive event: {event_type}")

                await self._handle_event(event)

        except websockets.exceptions.ConnectionClosed:
            logging.info("WebSocket closed")
        except Exception as e:
            logging.error(f"message processing error: {e}")

    async def _handle_event(self, event: Dict[str, Any]) -> None:
        event_type = event.get("type")

        match event_type:
            case "error":
                error_info = event.get('error', {})
                logging.error(f"server error: {error_info}")

            case "session.created":
                session_id = event.get('session', {}).get('id')
                logging.info(f"session created, id: {session_id}")

            case "session.updated":
                session_id = event.get('session', {}).get('id')
                logging.info(f"session updated, id: {session_id}")

            case "input_text_buffer.committed":
                item_id = event.get('item_id')
                logging.debug(f"text buffer committed, item id: {item_id}")

            case "input_text_buffer.cleared":
                logging.debug("text buffer cleared")

            case "response.created":
                self._current_response_id = event.get("response", {}).get("id")
                self._is_responding = True
                logging.info(f"response created, id: {self._current_response_id}")

            case "response.output_item.added":
                self._current_item_id = event.get("item", {}).get("id")
                logging.info(f"output item added, id: {self._current_item_id}")

            case "response.audio.delta":
                await self._handle_audio_delta(event)

            case "response.audio.done":
                logging.info("audio generated done")

            case "response.done":
                self._reset_response_state()
                logging.info("response done")

            case "session.finished":
                logging.info("session finished")

    async def _handle_audio_delta(self, event: Dict[str, Any]) -> None:
        if not self.audio_callback:
            return

        try:
            audio_data = event.get("delta", "")
            if audio_data:
                audio_bytes = base64.b64decode(audio_data)
                self.audio_callback(audio_bytes)
        except Exception as e:
            logging.error(f"audio data processing failed: {e}")

    def _reset_response_state(self) -> None:
        self._is_responding = False
        self._current_response_id = None
        self._current_item_id = None


    async def close(self) -> None:
        if self.ws:
            await self.ws.close()
            logging.info("WebSocket closed")
_tts_config = TTSConfig()
_audio_manager: Optional[AudioManager] = None

def _audio_callback(audio_bytes: bytes) -> None:
    global _audio_manager
    if _audio_manager:
        _audio_manager.play_audio(audio_bytes)


async def _produce_text(client: TTSRealtimeClient) -> None:
    text_fragments = [
        '但是...听到这样的命令，身体竟然有点颤抖的感觉...这种被羞辱的冲动',
        '深吸一口气，然后用最软糯的声音小声地说爸爸操我',
        '...爸爸...草我...声音小得像蚊子哼哼，脸颊红得要滴血了',
        '说完后整个人都缩起来，像只受惊的小猫，眼神却带着一丝奇异的期待',
    ]

    logging.info("start sending text fragments")
    for i, text in enumerate(text_fragments, 1):
        logging.info(f"sending fragment {i}/{len(text_fragments)}")
        await client.append_text(text)
        await asyncio.sleep(0.1) 

    await asyncio.sleep(1.0)
    await client.finish_session()

async def _run_demo() -> None:
    global _audio_manager, _tts_config

    audio_config = AudioConfig()
    _audio_manager = AudioManager(audio_config)
    _audio_manager.start_stream()

    try:
        config = TTSConfig.from_env()
        config.voice = "Cherry"
        config.language_type = "Chinese"

        client = TTSRealtimeClient(
            config=config,
            audio_callback=_audio_callback
        )

        await client.connect()

        consumer_task = asyncio.create_task(client.handle_messages())
        producer_task = asyncio.create_task(_produce_text(client))

        await producer_task

        await asyncio.sleep(5)

        await client.close()
        consumer_task.cancel()

    finally:    
        if _audio_manager:
            os.makedirs("outputs", exist_ok=True)
            output_file = os.path.join("outputs", "qwen_tts_output.wav")
            _audio_manager.save_to_file(output_file)
            _audio_manager.cleanup()

def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("start QwenTTS realtime client demo")
    asyncio.run(_run_demo())

if __name__ == "__main__":
    main() 