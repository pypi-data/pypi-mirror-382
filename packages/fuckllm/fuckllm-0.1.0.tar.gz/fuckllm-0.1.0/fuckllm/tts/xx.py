import asyncio
import websockets
import json
import base64
import time
import os
import asyncio
import logging
import wave
import pyaudio
from typing import Optional, Callable, Dict, Any
from enum import Enum


class SessionMode(Enum):
    SERVER_COMMIT = "server_commit"
    COMMIT = "commit"


class TTSRealtimeClient:
    def __init__(
            self,
            base_url: str,
            api_key: str,
            voice: str = "Cherry",
            mode: SessionMode = SessionMode.SERVER_COMMIT,
            audio_callback: Optional[Callable[[bytes], None]] = None,
        language_type: str = "Auto"):
        self.base_url = base_url
        self.api_key = api_key
        self.voice = voice
        self.mode = mode
        self.ws = None
        self.audio_callback = audio_callback
        self.language_type = language_type

        # 当前回复状态
        self._current_response_id = None
        self._current_item_id = None
        self._is_responding = False


    async def connect(self) -> None:
        """与 TTS Realtime API 建立 WebSocket 连接。"""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        self.ws = await websockets.connect(self.base_url, additional_headers=headers)

        # 设置默认会话配置
        await self.update_session({
            "mode": self.mode.value,
            "voice": self.voice,
            "language_type": self.language_type,
            "response_format": "pcm",
            "sample_rate": 24000
        })


    async def send_event(self, event) -> None:
        """发送事件到服务器。"""
        event['event_id'] = "event_" + str(int(time.time() * 1000))
        print(f"发送事件: type={event['type']}, event_id={event['event_id']}")
        await self.ws.send(json.dumps(event))


    async def update_session(self, config: Dict[str, Any]) -> None:
        """更新会话配置。"""
        event = {
            "type": "session.update",
            "session": config
        }
        print("更新会话配置: ", event)
        await self.send_event(event)


    async def append_text(self, text: str) -> None:
        """向 API 发送文本数据。"""
        event = {
            "type": "input_text_buffer.append",
            "text": text
        }
        await self.send_event(event)


    async def commit_text_buffer(self) -> None:
        """提交文本缓冲区以触发处理。"""
        event = {
            "type": "input_text_buffer.commit"
        }
        await self.send_event(event)


    async def clear_text_buffer(self) -> None:
        """清除文本缓冲区。"""
        event = {
            "type": "input_text_buffer.clear"
        }
        await self.send_event(event)


    async def finish_session(self) -> None:
        """结束会话。"""
        event = {
            "type": "session.finish"
        }
        await self.send_event(event)


    async def handle_messages(self) -> None:
        """处理来自服务器的消息。"""
        try:
            async for message in self.ws:
                event = json.loads(message)
                event_type = event.get("type")

                if event_type != "response.audio.delta":
                    print(f"收到事件: {event_type}")

                if event_type == "error":
                    print("错误: ", event.get('error', {}))
                    continue
                elif event_type == "session.created":
                    print("会话创建，ID: ", event.get('session', {}).get('id'))
                elif event_type == "session.updated":
                    print("会话更新，ID: ", event.get('session', {}).get('id'))
                elif event_type == "input_text_buffer.committed":
                    print("文本缓冲区已提交，项目ID: ", event.get('item_id'))
                elif event_type == "input_text_buffer.cleared":
                    print("文本缓冲区已清除")
                elif event_type == "response.created":
                    self._current_response_id = event.get("response", {}).get("id")
                    self._is_responding = True
                    print("响应已创建，ID: ", self._current_response_id)
                elif event_type == "response.output_item.added":
                    self._current_item_id = event.get("item", {}).get("id")
                    print("输出项已添加，ID: ", self._current_item_id)
                # 处理音频增量
                elif event_type == "response.audio.delta" and self.audio_callback:
                    audio_bytes = base64.b64decode(event.get("delta", ""))
                    self.audio_callback(audio_bytes)
                elif event_type == "response.audio.done":
                    print("音频生成完成")
                elif event_type == "response.done":
                    self._is_responding = False
                    self._current_response_id = None
                    self._current_item_id = None
                    print("响应完成")
                elif event_type == "session.finished":
                    print("会话已结束")

        except websockets.exceptions.ConnectionClosed:
            print("连接已关闭")
        except Exception as e:
            print("消息处理出错: ", str(e))


    async def close(self) -> None:
        """关闭 WebSocket 连接。"""
        if self.ws:
            await self.ws.close()



# QwenTTS 服务配置
URL = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime?model=qwen3-tts-flash-realtime"
# 若没有配置环境变量，请用百炼API Key将下行替换为：API_KEY="sk-xxx",
API_KEY = os.getenv("ali_api_key")

if not API_KEY:
    raise ValueError("Please set ali_api_key environment variable")

# 收集音频数据
_audio_chunks = []
# 实时播放相关
_AUDIO_SAMPLE_RATE = 24000
_audio_pyaudio = pyaudio.PyAudio()
_audio_stream = None  # 将在运行时打开

def _audio_callback(audio_bytes: bytes):
    """TTSRealtimeClient 音频回调: 实时播放并缓存"""
    global _audio_stream
    if _audio_stream is not None:
        try:
            _audio_stream.write(audio_bytes)
        except Exception as exc:
            logging.error(f"PyAudio playback error: {exc}")
    _audio_chunks.append(audio_bytes)
    logging.info(f"Received audio chunk: {len(audio_bytes)} bytes")

def _save_audio_to_file(filename: str = "output.wav", sample_rate: int = 24000) -> bool:
    """将收集到的音频数据保存为 WAV 文件"""
    if not _audio_chunks:
        logging.warning("No audio data to save")
        return False

    try:
        audio_data = b"".join(_audio_chunks)
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)  # 单声道
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data)
        logging.info(f"Audio saved to: {filename}")
        return True
    except Exception as exc:
        logging.error(f"Failed to save audio: {exc}")
        return False

async def _produce_text(client: TTSRealtimeClient):
    """向服务器发送文本片段"""
    text_fragments = [
        '但是...听到这样的命令，身体竟然有点颤抖的感觉...这种被羞辱的冲动',
        '深吸一口气，然后用最软糯的声音小声地说爸爸操我',
        '...爸爸...草我...声音小得像蚊子哼哼，脸颊红得要滴血了',
        '说完后整个人都缩起来，像只受惊的小猫，眼神却带着一丝奇异的期待',
    ]

    logging.info("Sending text fragments…")
    for text in text_fragments:
        logging.info(f"Sending fragment: {text}")
        await client.append_text(text)
        await asyncio.sleep(0.1)  # 片段间稍作延时

    # 等待服务器完成内部处理后结束会话
    await asyncio.sleep(1.0)
    await client.finish_session()

async def _run_demo():
    """运行完整 Demo"""
    global _audio_stream
    # 打开 PyAudio 输出流
    _audio_stream = _audio_pyaudio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=_AUDIO_SAMPLE_RATE,
        output=True,
        frames_per_buffer=1024
    )

    client = TTSRealtimeClient(
        base_url=URL,
        api_key=API_KEY,
        voice="Cherry",
        language_type="Chinese", # 建议与文本语种一致，以获得正确的发音和自然的语调。
        mode=SessionMode.SERVER_COMMIT,
        audio_callback=_audio_callback
    )

    # 建立连接
    await client.connect()

    # 并行执行消息处理与文本发送
    consumer_task = asyncio.create_task(client.handle_messages())
    producer_task = asyncio.create_task(_produce_text(client))

    await producer_task  # 等待文本发送完成

    # 额外等待，确保所有音频数据收取完毕
    await asyncio.sleep(5)

    # 关闭连接并取消消费者任务
    await client.close()
    consumer_task.cancel()

    # 关闭音频流
    if _audio_stream is not None:
        _audio_stream.stop_stream()
        _audio_stream.close()
    _audio_pyaudio.terminate()

    # 保存音频数据
    os.makedirs("outputs", exist_ok=True)
    _save_audio_to_file(os.path.join("outputs", "qwen_tts_output.wav"))

def main():
    """同步入口"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("Starting QwenTTS Realtime Client demo…")
    asyncio.run(_run_demo())

if __name__ == "__main__":
    main() 