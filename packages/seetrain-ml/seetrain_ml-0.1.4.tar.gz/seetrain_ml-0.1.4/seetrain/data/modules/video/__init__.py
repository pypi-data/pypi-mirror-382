#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Union, List, Tuple, Optional
from io import BytesIO
import numpy as np


def convert_size(size=None):
    """将size转换为视频的size"""
    if size is None:
        return None

    elif isinstance(size, int):
        return size

    elif isinstance(size, (list, tuple)) and len(size) in [1, 2]:
        size = tuple(size)
        width = int(size[0]) if size[0] is not None else None
        height = int(size[1]) if len(size) > 1 and size[1] is not None else None

        return (width, height) if len(size) == 2 else width

    raise ValueError("seetrain.Video - param `size` must be a list (with 2 or 1 elements) or an int")


def is_pytorch_tensor_typename(typename: str) -> bool:
    return typename.startswith("torch.") and ("Tensor" in typename or "Variable" in typename)


def get_full_typename(o: any) -> any:
    """Determine types based on type names.

    Avoids needing to import (and therefore depend on) PyTorch, TensorFlow, etc.
    """
    instance_name = o.__class__.__module__ + "." + o.__class__.__name__
    if instance_name in ["builtins.module", "__builtin__.module"]:
        return o.__name__
    else:
        return instance_name


class Video:
    ACCEPT_FORMAT = ["mp4", "avi", "mov", "mkv", "wmv", "flv", "webm"]

    def __init__(
            self,
            data_or_path: "VideoDataOrPathType",
            fps: int = 30,
            caption: str = None,
            file_type: str = None,
            size: Union[int, list, tuple] = None,
            max_frames: int = None
    ):
        try:
            import cv2
            import numpy as np
        except ImportError:
            raise ImportError(
                "opencv-python and numpy are required for Video class, you can install them by `pip install opencv-python numpy`"
            )
        
        self.format = self.__convert_file_type(file_type)
        self.size = convert_size(size)
        self.caption = caption
        self.fps = fps
        self.max_frames = max_frames

        # 判断数据类型
        if isinstance(data_or_path, str):
            try:
                self.cap = cv2.VideoCapture(data_or_path)
                if not self.cap.isOpened():
                    raise ValueError(f"Invalid video path: {data_or_path}")
                self.frames = self.__extract_frames_from_capture(self.cap)
                self.cap.release()
            except Exception as e:
                raise ValueError(f"Invalid video path: {data_or_path}") from e
        elif isinstance(data_or_path, np.ndarray):
            # 如果输入为numpy array (shape: [frames, height, width, channels] 或 [frames, height, width])
            try:
                if data_or_path.ndim == 4 or data_or_path.ndim == 3:
                    self.frames = self.__process_numpy_frames(data_or_path)
                else:
                    raise TypeError("Invalid numpy array: the numpy array must be 3D or 4D with shape (frames, height, width) or (frames, height, width, channels).")
            except Exception as e:
                raise TypeError("Invalid numpy array for the video") from e
        elif hasattr(data_or_path, 'read') and hasattr(data_or_path, 'isOpened'):
            # 如果输入为cv2.VideoCapture对象
            try:
                self.frames = self.__extract_frames_from_capture(data_or_path)
            except Exception as e:
                raise TypeError("Invalid cv2.VideoCapture object for the video") from e
        elif is_pytorch_tensor_typename(get_full_typename(data_or_path)):
            # 如果输入为pytorch tensor
            try:
                import torch
                import torchvision
            except ImportError:
                raise TypeError(
                    "seetrain.Video requires `torch` and `torchvision` when process torch.tensor data. "
                    "Install with 'pip install torch torchvision'."
                )
            if hasattr(data_or_path, "requires_grad") and data_or_path.requires_grad:
                data_or_path = data_or_path.detach()
            if hasattr(data_or_path, "dtype") and str(data_or_path.dtype) == "torch.uint8":
                data_or_path = data_or_path.to(float)
            
            # 假设tensor shape为 [frames, channels, height, width] 或 [frames, height, width]
            if data_or_path.dim() == 4:  # [frames, channels, height, width]
                frames = data_or_path.permute(0, 2, 3, 1).cpu().numpy()  # 转换为 [frames, height, width, channels]
            elif data_or_path.dim() == 3:  # [frames, height, width]
                frames = data_or_path.cpu().numpy()
            else:
                raise TypeError("Invalid tensor shape: must be 3D or 4D tensor")
            
            self.frames = self.__process_numpy_frames(frames)
        else:
            # 以上都不是，则报错
            raise TypeError(
                "Unsupported video type. Please provide a valid path, numpy array, cv2.VideoCapture, or torch.Tensor."
            )

        # 调整视频大小
        if self.size is not None:
            self.frames = self.__resize_frames(self.frames, self.size)

    def __convert_file_type(self, file_type: str = None):
        """转换file_type，并检测file_type是否正确"""
        if file_type is None:
            file_type = "mp4"

        if file_type not in self.ACCEPT_FORMAT:
            raise ValueError(f"file_type must be one of {self.ACCEPT_FORMAT}")

        return file_type

    def __extract_frames_from_capture(self, cap) -> List[np.ndarray]:
        """从cv2.VideoCapture对象中提取帧"""
        frames = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if self.max_frames and frame_count >= self.max_frames:
                break
                
            frames.append(frame)
            frame_count += 1
        
        if not frames:
            raise ValueError("No frames found in video")
            
        return frames

    def __process_numpy_frames(self, frames_array: np.ndarray) -> List[np.ndarray]:
        """处理numpy数组格式的帧数据"""
        frames = []
        
        for i in range(frames_array.shape[0]):
            if self.max_frames and i >= self.max_frames:
                break
                
            frame = frames_array[i]
            
            # 确保帧数据在正确的范围内
            if frame.dtype != np.uint8:
                if frame.max() <= 1.0:
                    frame = (frame * 255).astype(np.uint8)
                else:
                    frame = np.clip(frame, 0, 255).astype(np.uint8)
            
            frames.append(frame)
        
        if not frames:
            raise ValueError("No valid frames found in numpy array")
            
        return frames

    def __resize_frames(self, frames: List[np.ndarray], size) -> List[np.ndarray]:
        """调整视频帧大小"""
        if size is None:
            return frames

        import cv2
        resized_frames = []
        
        for frame in frames:
            if isinstance(size, int):
                # 保持宽高比，按比例缩放
                h, w = frame.shape[:2]
                if max(h, w) > size:
                    scale = size / max(h, w)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    resized_frame = cv2.resize(frame, (new_w, new_h))
                else:
                    resized_frame = frame
            elif isinstance(size, (list, tuple)):
                size = tuple(size)
                if all(size):
                    resized_frame = cv2.resize(frame, size)
                elif size[0] is not None:
                    h, w = frame.shape[:2]
                    scale = size[0] / w
                    new_h = int(h * scale)
                    resized_frame = cv2.resize(frame, (size[0], new_h))
                elif size[1] is not None:
                    h, w = frame.shape[:2]
                    scale = size[1] / h
                    new_w = int(w * scale)
                    resized_frame = cv2.resize(frame, (new_w, size[1]))
                else:
                    resized_frame = frame
            else:
                resized_frame = frame
                
            resized_frames.append(resized_frame)
        
        return resized_frames

    def get_frames(self) -> List[np.ndarray]:
        """获取视频帧列表"""
        return self.frames

    def get_frame_count(self) -> int:
        """获取帧数"""
        return len(self.frames)

    def get_frame_size(self) -> Tuple[int, int]:
        """获取帧尺寸 (width, height)"""
        if self.frames:
            h, w = self.frames[0].shape[:2]
            return (w, h)
        return (0, 0)

    def get_data(self):
        """获取视频数据，用于日志系统"""
        return self.to_bytes()

    def to_bytes(self) -> bytes:
        """将视频转换为二进制数据"""
        if not self.frames:
            raise ValueError("No frames to encode")
        
        import cv2
        import os
        
        # 使用用户设置的max_frames，如果没有设置则使用默认值
        max_frames = self.max_frames if self.max_frames is not None else 300
        frames_to_process = self.frames[:max_frames] if len(self.frames) > max_frames else self.frames
        
        # 创建临时视频写入器，使用高效的H264编码器
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H264编码器
        temp_path = '/tmp/temp_video.mp4'
        
        # 获取帧尺寸
        h, w = frames_to_process[0].shape[:2]
        
        # 创建视频写入器
        out = cv2.VideoWriter(temp_path, fourcc, self.fps, (w, h))
        
        # 设置压缩参数以减少文件大小
        if hasattr(out, 'set'):
            out.set(cv2.VIDEOWRITER_PROP_QUALITY, 25)  # 设置质量 (0-100)
        
        try:
            # 写入所有帧
            for frame in frames_to_process:
                out.write(frame)
            
            out.release()
            
            # 读取生成的视频文件
            with open(temp_path, 'rb') as f:
                video_bytes = f.read()
            
            # 删除临时文件
            os.remove(temp_path)
            
            return video_bytes
            
        except Exception as e:
            # 确保释放资源
            out.release()
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e

    def save(self, output_path: str) -> None:
        """保存视频到文件"""
        if not self.frames:
            raise ValueError("No frames to save")
        
        import cv2
        
        # 使用用户设置的max_frames，如果没有设置则使用所有帧
        max_frames = self.max_frames if self.max_frames is not None else len(self.frames)
        frames_to_process = self.frames[:max_frames] if len(self.frames) > max_frames else self.frames
        
        # 获取帧尺寸
        h, w = frames_to_process[0].shape[:2]
        
        # 根据文件扩展名选择编码器
        if output_path.lower().endswith('.mp4'):
            fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H264编码器
        elif output_path.lower().endswith('.avi'):
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
        else:
            fourcc = cv2.VideoWriter_fourcc(*'avc1')  # 默认使用H264
        
        # 创建视频写入器
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (w, h))
        
        # 设置压缩参数以减少文件大小
        if hasattr(out, 'set'):
            out.set(cv2.VIDEOWRITER_PROP_QUALITY, 25)  # 设置质量 (0-100)
        
        try:
            # 写入所有帧
            for frame in frames_to_process:
                out.write(frame)
        finally:
            out.release()


# 类型定义
VideoDataOrPathType = Union[str, np.ndarray, object]  # object for cv2.VideoCapture
