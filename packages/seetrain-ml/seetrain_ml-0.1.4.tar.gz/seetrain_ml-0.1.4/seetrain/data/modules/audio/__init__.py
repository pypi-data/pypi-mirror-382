#!/usr/bin/env python
# -*- coding: utf-8 -*-
from io import BytesIO
from typing import Union
import numpy as np

# 类型定义
AudioDataOrPathType = Union[str, np.ndarray]

class Audio:
    # 支持的numpy数据类型
    SF_SUPPORT_DTYPE = ['float32', 'float64', 'int16', 'int32', 'int64']
    
    def __init__(self, 
                 data_or_path: AudioDataOrPathType,
                 sample_rate: int = 44100,
                 caption: str = None):
        try:
            import soundfile as sf
            import numpy as np
        except ImportError:
            raise ImportError("pydub is required for Audio class, you can install it by `pip install pydub`")
        self.sample_rate = sample_rate
        self.caption = caption
        
        if isinstance(data_or_path, str):
           try:
                audio_data, self.sample_rate = sf.read(data_or_path)
                audio_data = audio_data.T
           except Exception as e:
                raise ValueError(f"Invalid audio path: {data_or_path}") from e
        elif isinstance(data_or_path, np.ndarray):
            # 如果输入为numpy array ，要求输入为 (num_channels, num_frames) 的形式
            # 支持单声道 或 双声道 两种形式

            if data_or_path.dtype not in self.SF_SUPPORT_DTYPE:
                e = (
                    f"Invalid numpy array for the audio data, support dtype is {self.SF_SUPPORT_DTYPE}, "
                    f"but got {data_or_path.dtype}"
                )
                raise TypeError(e)

            # 如果data_or_path是一维, 则reshape为2维
            if len(data_or_path.shape) == 1:
                data_or_path = data_or_path.reshape(1, -1)

            # 获取通道数
            num_channels = data_or_path.shape[0]

            if num_channels != 2 and num_channels != 1:
                raise TypeError("Invalid numpy array for the audio data, support shape is (num_channels, num_frames)")
            if sample_rate is None:
                raise TypeError("sample_rate must be provided when input is numpy array while constructing Audio()")
            audio_data = data_or_path
        else:
            raise TypeError("Unsupported audio type. Please provide a valid path or numpy array.")
        
        self.audio_data = audio_data
      
        
    def to_bytes(self, format: str = 'WAV'):
        """将音频转换为二进制数据
        
        Args:
            format: 输出格式，支持 'WAV', 'MP3', 'FLAC' 等
        Returns:
            bytes: 音频的二进制数据
        """
        try:
            import soundfile as sf
        except ImportError:
            raise ImportError("soundfile is required for to_bytes method")
        
        buf = BytesIO()
        
        # 将音频数据转置回 (num_frames, num_channels) 格式，因为soundfile期望这种格式
        audio_data_for_write = self.audio_data.T
        
        # 根据格式写入数据
        if format.upper() == 'WAV':
            sf.write(buf, audio_data_for_write, self.sample_rate, format='WAV')
        elif format.upper() == 'FLAC':
            sf.write(buf, audio_data_for_write, self.sample_rate, format='FLAC')
        elif format.upper() == 'MP3':
            # MP3格式需要特殊处理，soundfile可能不支持直接写入MP3
            # 这里先写入WAV格式，如果需要MP3可以后续添加转换
            sf.write(buf, audio_data_for_write, self.sample_rate, format='WAV')
        else:
            # 默认使用WAV格式
            sf.write(buf, audio_data_for_write, self.sample_rate, format='WAV')
        
        buf.seek(0)
        return buf.getvalue()
        