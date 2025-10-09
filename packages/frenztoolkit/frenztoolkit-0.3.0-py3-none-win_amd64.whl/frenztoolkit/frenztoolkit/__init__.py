"""
Frenz Streaming Toolkit
A toolkit for streaming data from Frenz Brainband
"""

__version__ = "0.2.6"

from .scanner import Scanner
from .streamer import Streamer, validate_product_key, check_latest_version

__all__ = ["Scanner", "Streamer", "validate_product_key", "check_latest_version"] 