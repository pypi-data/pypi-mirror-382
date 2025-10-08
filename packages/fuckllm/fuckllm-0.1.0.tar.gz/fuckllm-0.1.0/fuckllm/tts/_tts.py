import os
import threading
import asyncio
import time
from typing import Optional, List, Dict, Iterable

import dashscope
from dashscope import Generation
from dashscope.audio.tts_v2 import SpeechSynthesizer, ResultCallback, VoiceEnrollmentService
from http import HTTPStatus
from utils import B64PCMPlayer
import logging

class TTS:
    def __init__(self,
                 api_key: Optional[str] = None,
                 default_model: str = 'cosyvoice-v2',
                 default_voice: str = 'longhua_v2') -> None:
        self.default_model = default_model
        self.default_voice = default_voice
        api_key = api_key or os.getenv('DASHSCOPE_API_KEY') or os.getenv('ali_api_key')
        if not api_key:
            raise RuntimeError('DashScope API key not set. Set env DASHSCOPE_API_KEY or pass api_key explicitly.')
        dashscope.api_key = api_key
        self.api_key = api_key

    def synthesize(self,
                   text: str,
                   out: str = 'result.mp3',
                   model: Optional[str] = None,
                   voice: Optional[str] = None,
                   **kwargs) -> str:
        model = model or self.default_model
        voice = voice or self.default_voice
        s = SpeechSynthesizer(model=model, voice=voice, callback=None, **kwargs)
        audio = s.call(text)
        with open(out, 'wb') as f:
            f.write(audio)
        logging.info(f'[TTS] saved: {out}')
        logging.info('[Metric] requestId: {}, first package delay ms: {}'.format(
            s.get_last_request_id(), s.get_first_package_delay()))
        return out

    def synthesize_streaming(self,
                             text: str,
                             out: str = 'result.mp3',
                             model: Optional[str] = None,
                             voice: Optional[str] = None,
                             **kwargs) -> str:
        done = threading.Event()

        class _CB(ResultCallback):
            def on_open(self):
                self.file = open(out, 'wb')

            def on_complete(self):
                done.set()

            def on_close(self):
                try:
                    if hasattr(self, 'file') and self.file:
                        self.file.close()
                except Exception:
                    pass

            def on_error(self, message: str):
                logging.error(f'[TTS][error] {message}')
                done.set()

            def on_event(self, message):
                pass

            def on_data(self, data: bytes) -> None:
                if hasattr(self, 'file') and self.file:
                    self.file.write(data)

        model = model or self.default_model
        voice = voice or self.default_voice
        s = SpeechSynthesizer(model=model, voice=voice, callback=_CB(), **kwargs)
        s.call(text)
        done.wait()
        logging.info(f'[TTS] saved: {out}')
        logging.info('[Metric] requestId: {}, first package delay ms: {}'.format(
            s.get_last_request_id(), s.get_first_package_delay()))
        return out

    async def synthesize_chunks(self,
                                text_chunks: Iterable[str],
                                out: str = 'result.mp3',
                                delay: float = 0.1,
                                model: Optional[str] = None,
                                voice: Optional[str] = None,
                                **kwargs) -> str:
        class _AsyncCB(ResultCallback):
            def __init__(self, e: asyncio.Event):
                self._done = e
                self._file = open(out, 'wb')

            def on_complete(self):
                self._done.set()

            def on_close(self):
                try:
                    if self._file:
                        self._file.close()
                except Exception:
                    pass

            def on_error(self, message: str):
                logging.error(f'[TTS][error] {message}')
                self._done.set()

            def on_event(self, message):
                pass

            def on_data(self, data: bytes) -> None:
                if self._file:
                    self._file.write(data)

        model = model or self.default_model
        voice = voice or self.default_voice
        done = asyncio.Event()
        cb = _AsyncCB(done)
        s = SpeechSynthesizer(model=model, voice=voice, callback=cb, **kwargs)
        for t in text_chunks:
            s.streaming_call(t)
            await asyncio.sleep(delay)
        s.async_streaming_complete()
        await done.wait()
        logging.info(f'[TTS] saved: {out}')
        logging.info('[Metric] requestId: {}, first package delay ms: {}'.format(
            s.get_last_request_id(), s.get_first_package_delay()))
        return out

    def synthesize_batch(self,
                         tasks: List[Dict],
                         model: Optional[str] = None,
                         max_workers: int = 3) -> List[str]:
        """
        tasks: List[dict] like { 'text': str, 'voice': str='longhua_v2', 'out': str='result_i.mp3' }
        Use threads to avoid Windows multiprocessing pickling constraints and since tasks are IO-bound.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        model = model or self.default_model
        outs: List[str] = []

        def _work(task: Dict) -> str:
            text = task['text']
            voice = task.get('voice', self.default_voice)
            out = task.get('out', 'result.mp3')
            s = SpeechSynthesizer(model=model, voice=voice, callback=None)
            audio = s.call(text)
            with open(out, 'wb') as f:
                f.write(audio)
            logging.info('[Metric] requestId: {}, first package delay ms: {}'.format(
                s.get_last_request_id(), s.get_first_package_delay()))
            return out

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = [ex.submit(_work, t) for t in tasks]
            for fut in as_completed(futures):
                outs.append(fut.result())
        return outs

    def speak_llm_stream(self,
                         system_text: str,
                         query: str,
                         out: str = 'result.mp3',
                         llm_model: str = 'qwen-plus',
                         model: Optional[str] = None,
                         voice: Optional[str] = None,
                         **kwargs) -> str:
        model = model or self.default_model
        voice = voice or self.default_voice
        done = threading.Event()

        class _CB(ResultCallback):
            def on_open(self):
                self.file = open(out, 'wb')

            def on_complete(self):
                done.set()

            def on_close(self):
                try:
                    if hasattr(self, 'file') and self.file:
                        self.file.close()
                except Exception:
                    pass

            def on_event(self, message):
                pass

            def on_data(self, data: bytes) -> None:
                if hasattr(self, 'file') and self.file:
                    self.file.write(data)

            def on_error(self, message: str):
                logging.error(f'[TTS][error] {message}')
                done.set()

        cb = _CB()
        s = SpeechSynthesizer(model=model, voice=voice, callback=cb, **kwargs)

        messages = [
            {'role': 'system', 'content': system_text},
            {'role': 'user', 'content': query},
        ]

        responses = Generation.call(
            model=llm_model,
            messages=messages,
            result_format='message',
            stream=True,
            incremental_output=True,
        )

        for resp in responses:
            if resp.status_code == HTTPStatus.OK:
                chunk = resp.output.choices[0]['message']['content']
                if chunk:
                    s.streaming_call(chunk)
            else:
                logging.error(f'LLM error: {resp.status_code} {getattr(resp, "message", "")}')

        s.streaming_complete()
        done.wait()
        logging.info(f'[TTS] saved: {out}')
        logging.info('[Metric] requestId: {}, first package delay ms: {}'.format(
            s.get_last_request_id(), s.get_first_package_delay()))
        return out

    def create_clone_voice(self,
                           audio_url: str,
                           prefix: str = 'demo',
                           target_model: str = 'cosyvoice-v2') -> str:
        svc = VoiceEnrollmentService()
        vid = svc.create_voice(target_model=target_model, prefix=prefix, url=audio_url)
        return vid

    def list_voices(self,
                    prefix: Optional[str] = None,
                    page_index: int = 0,
                    page_size: int = 10):
        svc = VoiceEnrollmentService()
        return svc.list_voices(prefix=prefix, page_index=page_index, page_size=page_size)

    def delete_voices_by_prefix(self, prefix: str) -> int:
        svc = VoiceEnrollmentService()
        voices = svc.list_voices(prefix=prefix, page_index=0, page_size=50)
        count = 0
        for v in voices:
            svc.delete_voice(v['voice_id'])
            count += 1
        return count

    def synthesize_with_cloned_voice(self,
                                     text: str,
                                     voice_id: str,
                                     out: str = 'result.mp3',
                                     model: Optional[str] = None) -> str:
        model = model or self.default_model
        s = SpeechSynthesizer(model=model, voice=voice_id, callback=None)
        audio = s.call(text)
        with open(out, 'wb') as f:
            f.write(audio)
        return out

    def run_qwen_server_commit(self,
                               text_chunks: Iterable[str],
                               voice: str = 'Cherry',
                               response_format=None,
                               delay: float = 0.1,
                               save_file: bool = True) -> None:
        from dashscope.audio.qwen_tts_realtime import QwenTtsRealtime, QwenTtsRealtimeCallback, AudioFormat
        import pyaudio

        rf = response_format or AudioFormat.PCM_24000HZ_MONO_16BIT

        class _Callback(QwenTtsRealtimeCallback):
            def __init__(self):
                super().__init__()
                self.finish_event = threading.Event()
                self.pya = None
                self.player = None

            def on_open(self) -> None:
                self.pya = pyaudio.PyAudio()
                self.player = B64PCMPlayer(self.pya, save_file=save_file)

            def on_close(self, close_status_code, close_msg) -> None:
                if self.player:
                    self.player.wait_for_complete()
                    self.player.shutdown()
                if self.pya:
                    self.pya.terminate()
                    self.pya = None
                self.finish_event.set()

            def on_event(self, response: dict) -> None:
                try:
                    typ = response.get('type')
                    if typ == 'response.audio.delta':
                        data_b64 = response['delta']
                        if self.player:
                            self.player.add_data(data_b64)
                    if typ == 'session.finished':
                        self.finish_event.set()
                except Exception as e:
                    logging.error(f'[Error] {e}')
                    self.finish_event.set()

            def wait_for_complete(self):
                self.finish_event.wait()

        cb = _Callback()
        qrt = QwenTtsRealtime(model='qwen-tts-realtime', callback=cb)
        qrt.connect()
        qrt.update_session(
            voice=voice,
            response_format=rf,
            mode='server_commit',
        )
        for chunk in text_chunks:
            qrt.append_text(chunk)
            time.sleep(delay)
        qrt.finish()
        cb.wait_for_complete()
        qrt.close()

    def run_qwen_commit(self,
                        text_chunks: Iterable[str],
                        voice: str = 'Cherry',
                        response_format=None,
                        commit_interval: float = 2.0,
                        save_file: bool = True) -> None:
        from dashscope.audio.qwen_tts_realtime import QwenTtsRealtime, QwenTtsRealtimeCallback, AudioFormat
        import pyaudio

        rf = response_format or AudioFormat.PCM_24000HZ_MONO_16BIT

        class _Callback(QwenTtsRealtimeCallback):
            def __init__(self):
                super().__init__()
                self.finish_event = threading.Event()
                self.pya = None
                self.player = None

            def on_open(self) -> None:
                self.pya = pyaudio.PyAudio()
                self.player = B64PCMPlayer(self.pya, save_file=save_file)

            def on_close(self, close_status_code, close_msg) -> None:
                if self.player:
                    self.player.wait_for_complete()
                    self.player.shutdown()
                if self.pya:
                    self.pya.terminate()
                    self.pya = None
                self.finish_event.set()

            def on_event(self, response: dict) -> None:
                try:
                    typ = response.get('type')
                    if typ == 'response.audio.delta':
                        data_b64 = response['delta']
                        if self.player:
                            self.player.add_data(data_b64)
                    if typ == 'session.finished':
                        self.finish_event.set()
                except Exception as e:
                    logging.error(f'[Error] {e}')
                    self.finish_event.set()

            def wait_for_complete(self):
                self.finish_event.wait()

        cb = _Callback()
        qrt = QwenTtsRealtime(model='qwen-tts-realtime', callback=cb)
        qrt.connect()
        qrt.update_session(
            voice=voice,
            response_format=rf,
            mode='commit',
        )
        for chunk in text_chunks:
            qrt.append_text(chunk)
            qrt.commit()
            time.sleep(commit_interval)
        qrt.finish()
        cb.wait_for_complete()
        qrt.close()

if __name__ == '__main__':
    tts = TTS()
    texts=['小严我喜欢你','从遇到你的第一眼我就很喜欢你']