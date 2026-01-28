"""OCR Service Application"""

import os
import sys

# CRITICAL: Set Paddle environment BEFORE any paddle imports
# This must be done at module level before anything else
os.environ['PADDLE_WITH_ONEDNN'] = '0'
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['PADDLE_MKLDNN_FALLBACK_ON_MISMATCH'] = '1'
os.environ['PADDLE_INFERENCE_DISABLE_ONEDNN'] = '1'

# Force reload of paddle modules if already loaded
if 'paddle' in sys.modules:
    del sys.modules['paddle']
if 'paddleocr' in sys.modules:
    del sys.modules['paddleocr']
