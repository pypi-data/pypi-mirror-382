import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Optional, Literal
import aiohttp


VoiceType = Literal["Cherry", "Fable"]
LanguageType = Literal["Chinese", "English", "German", "Italian", "Portuguese", "Spanish", "Japanese", "Korean", "French", "Russian", "Auto"]
AudioFormat = Literal["mp3", "wav", "pcm"]


@dataclass
class SynthesisConfig:
    model: str = "qwen3-tts-flash"
    voice: VoiceType = "Cherry"
    language_type: LanguageType = "Chinese"
    response_format: AudioFormat = "mp3"
    sample_rate: int = 16000


@dataclass
class TTSResponse:
    url: str
    duration: Optional[float] = None
    size: Optional[int] = None


class TTSSynthesizer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ali_api_key")
        if not self.api_key:
            raise ValueError("api key is not set")
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

    async def synthesize(self, text: str, config: Optional[SynthesisConfig] = None) -> TTSResponse:
        if not config:
            config = SynthesisConfig()

        payload = {
            "model": config.model,
            "input": {
                "text": text,
                "voice": config.voice,
                "language_type": config.language_type
            }
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logging.error(f"TTS synthesis failed: {response.status} - {error_text}")
                    raise RuntimeError(f"TTS synthesis failed: {response.status}")

                result = await response.json()

                if "output" in result:
                    output = result["output"]
                    if "audio" in output and "url" in output["audio"]:
                        audio_info = output["audio"]
                        return TTSResponse(
                            url=audio_info["url"],
                            duration=audio_info.get("duration"),
                            size=audio_info.get("size")
                        )
                    else:
                        logging.error(f"no audio information in response: {result}")
                        raise RuntimeError("response has no audio information")
                else:
                    logging.error(f"unknown response format: {result}")
                    raise RuntimeError("unknown response format")

    def synthesize_sync(self, text: str, config: Optional[SynthesisConfig] = None) -> TTSResponse:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(lambda: asyncio.run(self.synthesize(text, config)))
            return future.result()

    async def synthesize_and_save(self, text: str, filename: str, config: Optional[SynthesisConfig] = None) -> str:
        response = await self.synthesize(text, config)

        async with aiohttp.ClientSession() as session:
            async with session.get(response.url) as audio_response:
                if audio_response.status != 200:
                    raise RuntimeError(f"download audio failed: {audio_response.status}")

                audio_data = await audio_response.read()

                os.makedirs(os.path.dirname(filename), exist_ok=True)

                with open(filename, 'wb') as f:
                    f.write(audio_data)

                logging.info(f"audio saved to: {filename}")
                return filename

    def synthesize_and_save_sync(self, text: str, filename: str, config: Optional[SynthesisConfig] = None) -> str:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(lambda: asyncio.run(self.synthesize_and_save(text, filename, config)))
            return future.result()


VOICE_PRESETS = {
    "温柔女声": SynthesisConfig(voice="Cherry", language_type="Chinese"),
    "故事声音": SynthesisConfig(voice="Fable", language_type="Chinese"),
}


async def synthesize_text(text: str, voice: str = "Cherry", language: str = "Chinese") -> TTSResponse:
    synthesizer = TTSSynthesizer()
    config = SynthesisConfig(voice=voice, language_type=language)
    return await synthesizer.synthesize(text, config)


def synthesize_text_sync(text: str, voice: str = "Cherry", language: str = "Chinese") -> TTSResponse:
    synthesizer = TTSSynthesizer()
    return synthesizer.synthesize_sync(text, SynthesisConfig(voice=voice, language_type=language))


async def synthesize_and_save_file(text: str, filename: str, voice: str = "Cherry", language: str = "Chinese") -> str:
    synthesizer = TTSSynthesizer()
    config = SynthesisConfig(voice=voice, language_type=language)
    return await synthesizer.synthesize_and_save(text, filename, config)


def synthesize_and_save_file_sync(text: str, filename: str, voice: str = "Cherry", language: str = "Chinese") -> str:
    synthesizer = TTSSynthesizer()
    return synthesizer.synthesize_and_save_sync(text, filename, SynthesisConfig(voice=voice, language_type=language))


async def test_synthesis():
    synthesizer = TTSSynthesizer()

    test_text = "你好，这是一个测试文本。"
    print(f"合成文本: {test_text}")

    try:
        response = await synthesizer.synthesize(test_text)
        print(f"音频URL: {response.url}")

        filename = "outputs/test_synthesis.wav"
        filepath = await synthesizer.synthesize_and_save(test_text, filename)
        print(f"音频已保存到: {filepath}")

        return response
    except Exception as e:
        print(f"合成失败: {e}")
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_synthesis())
