#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 类型和常量定义

# 指标类型常量
class MetricType:
    """指标类型常量"""
    TEXT = "text"
    NUMBER = "number"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


# 指标分类常量
class MetricCategory:
    """指标分类常量"""
    TEXT = "text"
    NUMERIC = "numeric"
    MEDIA = "media"


# 文件类型映射常量
class FileTypeMapping:
    """文件类型映射常量"""
    MAPPING = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'image': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'mp4': 'video/mp4',
        'video': 'video/mp4',
        'avi': 'video/avi',
        'mp3': 'audio/mpeg',
        'audio': 'audio/mpeg',
        'wav': 'audio/wav',
        'pdf': 'application/pdf',
        'txt': 'text/plain',
        'text': 'text/plain'
    }

    @classmethod
    def get_mime_type(cls, filename: str) -> str:
        """根据文件名获取MIME类型"""
        filename_lower = filename.lower()

        for keyword, mime_type in cls.MAPPING.items():
            if keyword in filename_lower:
                return mime_type

        # 默认返回二进制文件类型
        return 'application/octet-stream'
