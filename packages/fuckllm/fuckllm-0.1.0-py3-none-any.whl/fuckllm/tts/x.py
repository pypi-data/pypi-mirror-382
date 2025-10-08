import time
import pyaudio
import dashscope
from dashscope.api_entities.dashscope_response import SpeechSynthesisResponse
from dashscope.audio.tts_v2 import *
import os
from datetime import datetime
import uuid
def get_timestamp():
    now = datetime.now()
    formatted_timestamp = now.strftime("[%Y-%m-%d %H:%M:%S.%f]")
    return formatted_timestamp


model = "cosyvoice-v2"
voice = "longxiaochun_v2"
dashscope.api_key = os.getenv("ali_api_key")

# 定义回调接口
class Callback(ResultCallback):
    _player = None
    _stream = None
    _buffer = b''
    _id= str(int(time.time()))+uuid.uuid4().hex
    def on_open(self):
        print("连接建立：" + get_timestamp())
        self._player = pyaudio.PyAudio()
        self._stream = self._player.open(
            format=pyaudio.paInt16, channels=1, rate=22050, output=True
        )

    def on_complete(self):
        print("语音合成完成，所有合成结果已被接收：" + get_timestamp())
        with open(f"speech_{self._id}.mp3", "wb") as f:
            f.write(self._buffer)
    def on_error(self, message: str):
        print(f"语音合成出现异常：{message}")

    def on_close(self):
        print("连接关闭：" + get_timestamp())
        self._stream.stop_stream()
        self._stream.close()
        self._player.terminate()


    def on_event(self, message):
        pass

    def on_data(self, data: bytes) -> None:
        print(get_timestamp() + f" 二进制音频长度为：{len(data)}")
        self._stream.write(data)
        self._buffer += data    

callback = Callback()

test_text = [
     '但是...听到这样的命令，身体竟然有点颤抖的感觉...这种被羞辱的冲动',
     '深吸一口气，然后用最软糯的声音小声地说',
     '...爸爸...草我...声音小得像蚊子哼哼，脸颊红得要滴血了',
     '说完后整个人都缩起来，像只受惊的小猫，眼神却带着一丝奇异的期待',
 ]

SpeechSynthesizer
# 实例化SpeechSynthesizer，并在构造方法中传入模型（model）、音色（voice）等请求参数
synthesizer = SpeechSynthesizer(
    model=model,
    voice=voice,
    format=AudioFormat.PCM_22050HZ_MONO_16BIT,  
    callback=callback,
)


# 流式发送待合成文本。在回调接口的on_data方法中实时获取二进制音频
for text in test_text:
    synthesizer.streaming_call(text)
    time.sleep(0.1)
synthesizer.streaming_complete()

# 首次发送文本时需建立 WebSocket 连接，因此首包延迟会包含连接建立的耗时
print('[Metric] requestId为：{}，首包延迟为：{}毫秒'.format(
    synthesizer.get_last_request_id(),
    synthesizer.get_first_package_delay()))