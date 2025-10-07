"""
jafrdow - مكتبة Python لتنزيل مقاطع الفيديو من وسائل التواصل الاجتماعي
"""

from .core import JafrDow
from .exceptions import JafrDowError, APIError, DownloadError, NoVideoLinksError

__version__ = "0.1.0"
__author__ = "Jafr"
__description__ = "مكتبة بسيطة وقوية لتنزيل مقاطع الفيديو من وسائل التواصل الاجتماعي"

__all__ = [
    'JafrDow',
    'JafrDowError',
    'APIError', 
    'DownloadError',
    'NoVideoLinksError'
]