# import logging
# import os
# import pyaudio
# import dashscope
# from dashscope.audio.tts_v2 import *
# from datetime import datetime
# import uuid
# from typing import Optional
# import hashlib
# import json


# def get_timestamp() -> str:
#     return datetime.now().strftime("[%Y-%m-%d%H:%M:%S.%f]")


# class Callback(ResultCallback):
#     def __init__(self, file_path: str = "msg"):
#         self._player = None
#         self._stream = None
#         self._buffer = b""
#         self._id = get_timestamp() + uuid.uuid4().hex
#         self._file_path = file_path

#     def on_open(self):
#         self._player = pyaudio.PyAudio()
#         self._stream = self._player.open(
#             format=pyaudio.paInt16, channels=1, rate=22050, output=True
#         )

#     def on_complete(self):
#         with open(os.path.join(self._file_path, f"speech_{self._id}.pcm"), "wb") as f:
#             f.write(self._buffer)
#         logging.info("ali tts callback complete" + get_timestamp())

#     def on_error(self, message: str):
#         logging.error(f"ali tts callback error: {message}")

#     def on_close(self):
#         logging.info("ali tts callback close" + get_timestamp())
#         self._stream.stop_stream()
#         self._stream.close()
#         self._player.terminate()

#     def on_event(self, message):
#         pass

#     def on_data(self, data: bytes) -> None:
#         self._stream.write(data)
#         self._buffer += data


# class Talker:
#     def __init__(
#         self,
#         api_key: str,   
#         model: str,
#         voice: str,
#         format: Optional[AudioFormat] = AudioFormat.DEFAULT,
#         volume: Optional[int] = 50,
#         speech_rate: Optional[float] = 1.0,
#         pitch_rate: Optional[float] = 1.0,
#         headers: Optional[dict] = None,
#         callback: ResultCallback = Callback(),
#         workspace: Optional[str] = None,
#         url: Optional[str] = None,
#         additional_params: Optional[dict] = None,
#     ):
#         dashscope.api_key = api_key
#         self._speech_synthesize = SpeechSynthesizer(
#             model=model,
#             voice=voice,
#             format=format,
#             volume=volume,
#             speech_rate=speech_rate,
#             pitch_rate=pitch_rate,
#             headers=headers,
#             callback=callback,
#             workspace=workspace,
#             url=url,
#             additional_params=additional_params,
#         )
#         self.cfg= {
#             "model": model,
#             "voice": voice,
#             "format": str(format),
#             "volume": volume,
#             "speech_rate": speech_rate,
#             "pitch_rate": pitch_rate,
#         }

#     def _identifier(self, text: str) -> str:
#         kwargs = self.cfg.copy()
#         kwargs["text"] = text
#         return hashlib.sha256(json.dumps(kwargs).encode()).hexdigest()

    
#     def streaming_call(self,text:str):
#         self._speech_synthesize().streaming_call(text)
        
#     def streaming_complete(self):
#         self._speech_synthesize.streaming_complete()

# async def synthesizer_with_llm_v2():
#     from config import ali_config
#     from model import Chater

#     llm_cfg = ali_config()
#     llm_cfg.chat_cfg.stream = False
#     chater = Chater(llm_cfg.to_dict())
#     messages = [{"role": "user", "content": "请介绍一下你自己"}]

#     response = await chater.chat(messages)
#     model = "cosyvoice-v2"
#     voice = "longxiaochun_v2"
#     dashscope.api_key = os.getenv("ali_api_key")

#     synthesizer = SpeechSynthesizer(
#         model=model,
#         voice=voice,
#         format=AudioFormat.PCM_22050HZ_MONO_16BIT,
#         callback=Callback(),
#     )
#     text_content = ""
#     if chater.stream:
#         async for msg in response:
#             if msg.content:
#                 print(msg.content, end="", flush=True)
#                 synthesizer.streaming_call(msg.content)
#     else:
#         text_content = response.content
#         print(text_content)
#         synthesizer.streaming_call(response.content)

#     synthesizer.streaming_complete()
#     print("requestId: ", synthesizer.get_last_request_id())


# if __name__ == "__main__":
#     import asyncio

#     asyncio.run(synthesizer_with_llm_v2())
# coding=utf-8

import dashscope
from dashscope.audio.tts_v2 import *
import os

# 若没有将API Key配置到环境变量中，需将your-api-key替换为自己的API Key
dashscope.api_key = os.getenv("ali_api_key")

# 模型
model = "cosyvoice-v2"
# 音色
voice = "longxiaochun_v2"

# 实例化SpeechSynthesizer，并在构造方法中传入模型（model）、音色（voice）等请求参数
synthesizer = SpeechSynthesizer(model=model, voice=voice)
# 发送待合成文本，获取二进制音频
audio = synthesizer.call("今天天气怎么样？")
# 首次发送文本时需建立 WebSocket 连接，因此首包延迟会包含连接建立的耗时
print('[Metric] requestId为：{}，首包延迟为：{}毫秒'.format(
    synthesizer.get_last_request_id(),
    synthesizer.get_first_package_delay()))

# 将音频保存至本地
with open('output.mp3', 'wb') as f:
    f.write(audio)