import hashlib
import json
import os
import threading
import asyncio
import time
from typing import Any, Literal, Optional, List, Dict, Iterable
import dashscope
from dashscope import Generation
from http import HTTPStatus
import base64
import wave
import pyaudio
import logging
from utils import B64PCMPlayer
from concurrent.futures import ThreadPoolExecutor, as_completed
from dashscope.audio.tts_v2 import SpeechSynthesizer,AudioFormat,ResultCallback
from dashscope.api_entities.dashscope_response import SpeechSynthesisResponse
from dashscope.audio.tts import (
    ResultCallback as v1ResultCallback, 
    SpeechSynthesizer as v1SpeechSynthesizer, 
    SpeechSynthesisResult as v1SpeechSynthesisResult
)

from dashscope.audio.qwen_tts_realtime import (
    QwenTtsRealtime,
    QwenTtsRealtimeCallback,
    AudioFormat as QwenAudioFormat,
)
from dataclasses import dataclass
@dataclass
class SynthesisResult:
    source: Literal['api', 'cache']
    file_path: str
class AliTTS:
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "cosyvoice-v2",
        default_voice: str = "longhua_v2",
        output_dir: str = "output",
    ) -> None:
        self.default_model = default_model
        self.default_voice = default_voice
        api_key = api_key or os.getenv("DASHSCOPE_API_KEY") or os.getenv("ali_api_key")
        if not api_key:
            raise RuntimeError(
                "DashScope API key not set. Set env DASHSCOPE_API_KEY or pass api_key explicitly."
            )
        dashscope.api_key = api_key
        self.api_key = api_key
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _build_key(self, payload: Dict) -> str:
        data = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    def _get_cache_path(self, key: str, out_ext: str) -> str:
        return os.path.join(self.output_dir, f'{key}.{out_ext}')
    
    def cosyvoice_synthesize(
        self,
        text: str,
        model: str = "cosyvoice-v2",
        voice: str = "longxiaochun_v2",
        format: AudioFormat = AudioFormat.DEFAULT,
        **kwargs,
    ) -> SynthesisResult:
        out_ext = format.format if format!=AudioFormat.DEFAULT else "mp3"
        payload = {
            "model": model,
            "voice": voice,
            "text": text,
            "format": str(format),
            "extra": {k: v for k, v in kwargs.items() if k not in ("callback",) and v},
        }

        identifier=self._build_key(payload)
        cache_path = self._get_cache_path(identifier, out_ext)
        if os.path.exists(cache_path):
            return SynthesisResult(source='cache', file_path=cache_path)
        
        s = SpeechSynthesizer(model=model, voice=voice ,callback=None,**kwargs)
        audio = s.call(text)

        if audio is None:
            raise RuntimeError(f"TTS synthesis failed: audio data is None. This may be due to invalid parameters, service unavailability, or quota issues.")
        
        with open(cache_path, "wb") as f:
            f.write(audio)
        return SynthesisResult(source='api', file_path=cache_path)

    def cosyvoice_synthesize_streaming(
        self,
        text: str,
        model: str = "cosyvoice-v2",
        voice: str = "longxiaochun_v2",
        format: AudioFormat = AudioFormat.DEFAULT,
        **kwargs,
    ) -> SynthesisResult:
        done = threading.Event()
        out_ext = format.format if format!=AudioFormat.DEFAULT else "mp3"
        payload = {
            "model": model,
            "voice": voice,
            "text": text,
            "format": str(format),
            "extra": {k: v for k, v in kwargs.items() if k not in ("callback",) and v},
        }
        
        identifier=self._build_key(payload)
        cache_path = self._get_cache_path(identifier, out_ext)
        if os.path.exists(cache_path):
            return SynthesisResult(source='cache', file_path=cache_path)
        
        class _CB(ResultCallback):
            def on_open(self):
                os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
                self.file = open(cache_path, "wb")

            def on_complete(self):
                done.set()

            def on_close(self):
                try:
                    if hasattr(self, "file") and self.file:
                        self.file.close()
                except Exception:
                    pass

            def on_error(self, message: str):
                logging.error(f"[TTS][error] {message}")
                done.set()

            def on_event(self, message):
                print(f"[TTS][event] {message}")

            def on_data(self, data: bytes) -> None:
                if hasattr(self, "file") and self.file:
                    self.file.write(data)

        s = SpeechSynthesizer(model=model, voice=voice, callback=_CB(), **kwargs)
        s.call(text)
        done.wait()
        return SynthesisResult(source='api', file_path=cache_path)

    async def cosyvoice_synthesize_chunks(
        self,
        text_chunks: Iterable[str],
        model: str = "cosyvoice-v2",
        voice: str = "longxiaochun_v2",
        format: AudioFormat = AudioFormat.DEFAULT,
        delay: Optional[float]= 0.1,
        **kwargs,
    ) -> SynthesisResult:
        class _AsyncCB(ResultCallback):
            def __init__(self, e: asyncio.Event, path: str):
                self._done = e
                os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                self._file = open(path, "wb")

            def on_complete(self):
                self._done.set()

            def on_close(self):
                try:
                    if self._file:
                        self._file.close()
                except Exception:
                    pass

            def on_error(self, message: str):
                logging.error(f"[TTS][error] {message}")
                self._done.set()

            def on_event(self, message):
                pass

            def on_data(self, data: bytes) -> None:
                if self._file:
                    self._file.write(data)
        
        out_ext = format.format if format!=AudioFormat.DEFAULT else "mp3"
        if isinstance(text_chunks, (list, tuple)):
            chunks = list(text_chunks)
        else:
            chunks = list(text_chunks)
            
        joined_text = "".join(chunks)
        payload = {
            "model": model,
            "voice": voice,
            "format": str(format),
            "text": joined_text,
            "extra": {k: v for k, v in kwargs.items() if k not in ("callback",) and v},
        }
        if delay:
            payload["extra"]["delay"] = delay
        identifier=self._build_key(payload)
        cache_path = self._get_cache_path(identifier, out_ext)
        if os.path.exists(cache_path):
            return SynthesisResult(source='cache', file_path=cache_path)
        done = asyncio.Event()
        cb = _AsyncCB(done, cache_path)
        s = SpeechSynthesizer(model=model, voice=voice, callback=cb, **kwargs)
        for t in chunks:
            s.streaming_call(t)
            await asyncio.sleep(delay)
        s.async_streaming_complete()
        return SynthesisResult(source='api', file_path=cache_path)

    def synthesize_batch(
        self, tasks: List[Dict], max_workers: int = 3
    ) -> List[SynthesisResult]:

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = [ex.submit(self.cosyvoice_synthesize, **task) for task in tasks]
            return [fut.result() for fut in as_completed(futures)]

    def sambert_synthesize(
        self,
        model: str,
        text: str,
        callback: ResultCallback | None = None,
        workspace: str | None = None,
        **kwargs: Any
    ) -> SynthesisResult:
        class Callback(ResultCallback):
            def on_open(self):
                print('Speech synthesizer is opened.')

            def on_complete(self):
                print('Speech synthesizer is completed.')

            def on_error(self, response: SpeechSynthesisResponse):
                print('Speech synthesizer failed, response is %s' % (str(response)))

            def on_close(self):
                print('Speech synthesizer is closed.')

            def on_event(self, result: v1SpeechSynthesisResult):
                if result.get_audio_frame() is not None:
                    print('audio result length:', sys.getsizeof(result.get_audio_frame()))

                if result.get_timestamp() is not None:
                    print('timestamp result:', str(result.get_timestamp()))
        callback = Callback()
        v1SpeechSynthesizer.call(model=model,
                            text=text,
                            sample_rate=sample_rate,
                            callback=callback,
                            word_timestamp_enabled=True,
                            phoneme_timestamp_enabled=True)
    def speak_llm_stream(
        self,
        system_text: str,
        query: str,
        llm_model: str = "qwen-plus",
        model: str = "cosyvoice-v2",
        voice: str = "longxiaochun_v2",
        format: AudioFormat = AudioFormat.DEFAULT,
        **kwargs,
    ) -> str:
        done = threading.Event()

        class _CB(ResultCallback):
            def __init__(self):
                self._buffer = b""

            def on_open(self,):
                pass

            def on_data(self, data: bytes) -> None:
                self._buffer += data
        
            def on_error(self, message: str):
                logging.error(f"[TTS][error] {message}")
                done.set()
            
            def on_event(self, message):
                print(f"[TTS][event] {message}")
            
            def on_close(self) -> None:
                with open("output.mp3", "wb") as f:
                    f.write(self._buffer)

        cb = _CB()
        s = SpeechSynthesizer(model=model, voice=voice, callback=cb, **kwargs)

        messages = [
            {"role": "system", "content": system_text},
            {"role": "user", "content": query},
        ]

        responses = Generation.call(
            model=llm_model,
            messages=messages,
            result_format="message",
            stream=True,
            incremental_output=True,
        )
        joined_text = ""
        for resp in responses:
            if resp.status_code == HTTPStatus.OK:
                chunk = resp.output.choices[0]["message"]["content"]
                if chunk:
                    print(chunk,end="",flush=True)
                    joined_text += chunk
                    s.streaming_call(chunk)
            else:
                logging.error(
                    f'LLM error: {resp.status_code} {getattr(resp, "message", "")}'
                )
        out_ext = format.format if format!=AudioFormat.DEFAULT else "mp3"
        payload = {
            "model": model,
            "voice": voice,
            "format": str(format),
            "text": joined_text,
            "extra": {k: v for k, v in kwargs.items() if k not in ("callback",) and v},
        }

        identifier=self._build_key(payload)
        cache_path = self._get_cache_path(identifier, out_ext)
        s.streaming_complete()
        
        done.wait()
        return SynthesisResult(source='api', file_path=cache_path)

    def create_clone_voice(
        self, audio_url: str, prefix: str = "demo", target_model: str = "cosyvoice-v2"
    ) -> str:
        from dashscope.audio.tts_v2 import VoiceEnrollmentService
        svc = VoiceEnrollmentService()
        vid = svc.create_voice(target_model=target_model, prefix=prefix, url=audio_url)
        return vid

    def list_voices(
        self, prefix: Optional[str] = None, page_index: int = 0, page_size: int = 10
    ):
        from dashscope.audio.tts_v2 import VoiceEnrollmentService
        svc = VoiceEnrollmentService()
        return svc.list_voices(
            prefix=prefix, page_index=page_index, page_size=page_size
        )

    def delete_voices_by_prefix(self, prefix: str) -> int:
        from dashscope.audio.tts_v2 import VoiceEnrollmentService
        svc = VoiceEnrollmentService()
        voices = svc.list_voices(prefix=prefix, page_index=0, page_size=50)
        count = 0
        for v in voices:
            svc.delete_voice(v["voice_id"])
            count += 1
        return count

    def synthesize_with_cloned_voice(
        self,
        text: str,
        voice_id: str,
        format: AudioFormat = AudioFormat.DEFAULT,
        model: Optional[str] = None,
    ) -> str:
        model = model or self.default_model
        return self.synthesize(text=text, format=format, model=model, voice=voice_id)

    def run_qwen_server_commit(
        self,
        text_chunks: Iterable[str],
        model: str = "qwen-tts-realtime",
        voice: str = "longxiaochun_v2",
        response_format=QwenAudioFormat.PCM_24000HZ_MONO_16BIT,
        delay: float = 0.1,
        wav_sample_rate: int = 24000,
        **kwargs,
    ) -> SynthesisResult:
        text_joined = "".join(text_chunks)
        payload = {
            "model": model,
            "voice": voice,
            "format": str(response_format),
            "text": text_joined,
            "extra": {k: v for k, v in kwargs.items() if k not in ("callback",) and v},
        }
        if delay:
            payload["extra"]["delay"] = delay
        out_ext = response_format.format if response_format!=QwenAudioFormat.DEFAULT else "mp3"
        identifier=self._build_key(payload)
        cache_path = self._get_cache_path(identifier, out_ext)
        if os.path.exists(cache_path):
            
            return SynthesisResult(source='cache', file_path=cache_path)

        class _Callback(QwenTtsRealtimeCallback):
            def __init__(self):
                super().__init__()
                self.finish_event = threading.Event()
                self.pya = None
                self.player = None
                self.wav = None
                self.pcm = None

            def on_open(self) -> None:
                self.pya = pyaudio.PyAudio()
                self.player = B64PCMPlayer(self.pya,)
                os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
                self.wav = wave.open(cache_path, "wb")
                self.wav.setnchannels(1)
                self.wav.setframerate(wav_sample_rate)
                self.wav.setsampwidth(2)

            def on_close(self, close_status_code, close_msg) -> None:
                if self.player:
                    self.player.wait_for_complete()
                    self.player.shutdown()
                if self.pya:
                    self.pya.terminate()
                    self.pya = None
                if self.wav:
                    try:
                        self.wav.close()
                    except Exception:
                        pass
                if self.pcm:
                    try:
                        self.pcm.close()
                    except Exception:
                        pass
                self.finish_event.set()

            def on_event(self, response: dict) -> None:
                try:
                    typ = response.get("type")
                    if typ == "response.audio.delta":
                        data_b64 = response["delta"]
                        if self.player:
                            self.player.add_data(data_b64)
                        try:
                            raw = base64.b64decode(data_b64)
                            if self.wav:
                                self.wav.writeframes(raw)
                            if self.pcm:
                                self.pcm.write(raw)
                        except Exception:
                            pass
                    if typ == "session.finished":
                        self.finish_event.set()
                except Exception as e:
                    logging.error(f"[Error] {e}")
                    self.finish_event.set()

            def wait_for_complete(self):
                self.finish_event.wait()

        cb = _Callback()
        qrt = QwenTtsRealtime(model=model, callback=cb, **kwargs)
        qrt.connect()
        qrt.update_session(
            voice=voice,
            response_format=response_format,
            mode="server_commit",
        )
        for chunk in text_chunks:
            qrt.append_text(chunk)
            if delay:
                time.sleep(delay)
        qrt.finish()
        cb.wait_for_complete()
        qrt.close()
        return SynthesisResult(source='api', file_path=cache_path)

    def run_qwen_commit(
        self,
        text_chunks: Iterable[str],
        model: str = "qwen-tts-realtime",
        voice: str = "Cherry",
        response_format: QwenAudioFormat = QwenAudioFormat.PCM_24000HZ_MONO_16BIT,
        commit_interval: float = 2.0,
        wav_sample_rate: int = 24000,
        sample_rate: int = 24000,
        chunk_size_ms: int = 100,
        save_file: bool = False
    ) -> None:
        payload = {
            "model": model,
            "voice": voice,
            "format": str(response_format),
            "response_format": str(response_format),
            "commit_interval": commit_interval,
            "wav_sample_rate": wav_sample_rate,
            "sample_rate": sample_rate,
            "chunk_size_ms": chunk_size_ms,
            "save_file": save_file,
        }
        out_ext = response_format.format if response_format!=QwenAudioFormat.DEFAULT else "mp3"
        identifier=self._build_key(payload)
        cache_path = self._get_cache_path(identifier, out_ext)

        class _Callback(QwenTtsRealtimeCallback):
            def __init__(self):
                super().__init__()
                self.finish_event = threading.Event()
                self.pya = None
                self.player = None
                self.wav = None
                self.pcm = None

            def on_open(self) -> None:
                self.pya = pyaudio.PyAudio()
                self.player = B64PCMPlayer(self.pya, save_file=True)
                os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
                self.wav = wave.open(cache_path, "wb")
                self.wav.setnchannels(1)
                self.wav.setframerate(wav_sample_rate)
                self.wav.setsampwidth(2)

            def on_close(self, close_status_code, close_msg) -> None:
                if self.player:
                    self.player.wait_for_complete()
                    self.player.shutdown()
                if self.pya:
                    self.pya.terminate()
                    self.pya = None
                if self.wav:
                    try:
                        self.wav.close()
                    except Exception:
                        pass
                if self.pcm:
                    try:
                        self.pcm.close()
                    except Exception:
                        pass
                self.finish_event.set()

            def on_event(self, response: dict) -> None:
                try:
                    typ = response.get("type")
                    if typ == "response.audio.delta":
                        data_b64 = response["delta"]
                        if self.player:
                            self.player.add_data(data_b64)
                        try:
                            raw = base64.b64decode(data_b64)
                            if self.wav:
                                self.wav.writeframes(raw)
                            if self.pcm:
                                self.pcm.write(raw)
                        except Exception:
                            pass
                    if typ == "session.finished":
                        self.finish_event.set()
                except Exception as e:
                    logging.error(f"[Error] {e}")
                    self.finish_event.set()

            def wait_for_complete(self):
                self.finish_event.wait()

        cb = _Callback()
        qrt = QwenTtsRealtime(model="qwen-tts-realtime", callback=cb)
        qrt.connect()
        qrt.update_session(
            voice=voice,
            response_format=rf,
            mode="commit",
        )
        for chunk in text_chunks:
            qrt.append_text(chunk)
            qrt.commit()
            time.sleep(commit_interval)
        qrt.finish()
        cb.wait_for_complete()
        qrt.close()

if __name__ == "__main__":
    tts = AliTTS()
    # tts.run_qwen_commit(text_chunks=['小严我喜欢你', '从遇到你的第一眼我就很喜欢你'], voice='Cherry')
    # tts.run_qwen_server_commit(text_chunks=['小严我喜欢你', '从遇到你的第一眼我就很喜欢你'], voice='Cherry')
    # result = tts.cosyvoice_synthesize(text='小严我喜欢你,从遇到你的第一眼我就很喜欢你,hahahh就是这一点啊',)
    result = tts.cosyvoice_synthesize_streaming(text='小严我喜欢你,从遇到你的第一眼我就很喜欢你,hahahh就是这一点啊,你知道吗？', )
    # import asyncio
    # result = asyncio.run(tts.cosyvoice_synthesize_chunks(text_chunks=['小严我喜欢你', '从遇到你的第一眼我就很喜欢你'], delay=1))
    # result = tts.speak_llm_stream(system_text='你是一个AI助手', query='小严我喜欢你,从遇到你的第一眼我就很喜欢你', voice='Cherry')
    print(result)
    # tts.synthesize_streaming(text='小严我喜欢你,从遇到你的第一眼我就很喜欢你', out='result.wav', voice='Cherry')