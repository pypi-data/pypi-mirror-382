import contextlib
import pyaudio
import threading
import queue
import base64
from typing import Optional


class B64PCMPlayer:
    def __init__(
        self,
        pya: pyaudio.PyAudio,
        sample_rate:int=24000,
        chunk_size_ms:int=100,
        save_file:bool=False,
        out_file: Optional[str] = None,
    ):
        """
        pya: pyaudio.PyAudio
        sample_rate: int
        chunk_size_ms: int -> affect playback latency
        """
        self.pya = pya
        self.sample_rate = sample_rate
        self.chunk_size_bytes = chunk_size_ms * sample_rate * 2 // 1000
        self.player_stream = pya.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            output=True,
        )
        self.raw_audio_buffer: queue.Queue = queue.Queue()
        self.b64_audio_buffer: queue.Queue = queue.Queue()
        self.status = "playing"
        self.decoder_thread = threading.Thread(target=self.decoder_loop)
        self.player_thread = threading.Thread(target=self.player_loop)
        self.decoder_thread.start()
        self.player_thread.start()
        self.complete_event: Optional[threading.Event] = None
        self.save_file = save_file
        if self.save_file:
            self.out_file = open(out_file or "result.pcm", "wb")

    def decoder_loop(self):
        while self.status != "stop":
            recv_audio_b64 = None
            with contextlib.suppress(queue.Empty):
                recv_audio_b64 = self.b64_audio_buffer.get(timeout=0.1)
            if recv_audio_b64 is None:
                continue
            recv_audio_raw = base64.b64decode(recv_audio_b64)
            for i in range(0, len(recv_audio_raw), self.chunk_size_bytes):
                chunk = recv_audio_raw[i : i + self.chunk_size_bytes]
                self.raw_audio_buffer.put(chunk)
                if self.save_file:
                    self.out_file.write(chunk)

    def player_loop(self):
        while self.status != "stop":
            recv_audio_raw = None
            with contextlib.suppress(queue.Empty):
                recv_audio_raw = self.raw_audio_buffer.get(timeout=0.1)
            if recv_audio_raw is None:
                if self.complete_event:
                    self.complete_event.set()
                continue
            self.player_stream.write(recv_audio_raw)

    def cancel_playing(self):
        self.b64_audio_buffer.queue.clear()
        self.raw_audio_buffer.queue.clear()

    def add_data(self, data):
        self.b64_audio_buffer.put(data)

    def wait_for_complete(self):
        self.complete_event = threading.Event()
        self.complete_event.wait()
        self.complete_event = None

    def shutdown(self):
        self.status = "stop"
        self.decoder_thread.join()
        self.player_thread.join()
        self.player_stream.close()
        if self.save_file:
            self.out_file.close()
