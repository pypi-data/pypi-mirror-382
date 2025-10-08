# Copyright (c) 2025 Venkata Vikhyat Choppa
# Licensed under the Apache 2.0 License. See LICENSE file for details.

import logging
import hashlib

logger = logging.getLogger("quantstratforge")
logging.basicConfig(level=logging.INFO)

def add_watermark(text: str, key: str = "secret") -> str:
    wm = hashlib.md5(key.encode()).hexdigest()[:6]
    return f"{text} [WM:{wm}]"