# -*- coding: utf-8 -*-
from typing import Union, List
from .image import Image
from .audio import Audio
from .text import Text
from .video import Video

DataType = Union[
    int,
    float,
    str,
    Image,
    Audio,
    Video,
]

__all__ = ["DataType", "Image", "Audio", "Text", "Video"]