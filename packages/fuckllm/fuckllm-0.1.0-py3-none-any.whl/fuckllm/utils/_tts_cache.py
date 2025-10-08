import hashlib
import json
import os
import shutil
from typing import Dict, Optional


class TTSCache:
    def __init__(self, enabled: bool = True, cache_dir: str = 'tts_cache') -> None:
        self.enabled = enabled
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def build_key(self, payload: Dict) -> str:
        data = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    def cache_path(self, key: str, fmt: str) -> str:
        ext = 'wav' if fmt == 'wav' else ('mp3' if fmt == 'mp3' else fmt)
        return os.path.join(self.cache_dir, f'{key}.{ext}')

    def plan(self, payload: Dict, fmt: str, out: str) -> Dict:
        if not self.enabled:
            return {'hit': False, 'hit_out': None, 'target_path': out, 'cache_path': None}
        key = self.build_key(payload)
        cpath = self.cache_path(key, fmt)
        if os.path.exists(cpath):
            if os.path.abspath(cpath) != os.path.abspath(out):
                os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
                shutil.copyfile(cpath, out)
            return {'hit': True, 'hit_out': out, 'target_path': None, 'cache_path': cpath}
        return {'hit': False, 'hit_out': None, 'target_path': cpath + '.part', 'cache_path': cpath}

    def finalize(self, cache_path: Optional[str], target_path: str, out: str) -> None:
        if not self.enabled:
            return
        if not cache_path:
            return
        os.replace(target_path, cache_path)
        if os.path.abspath(cache_path) != os.path.abspath(out):
            os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
            shutil.copyfile(cache_path, out)