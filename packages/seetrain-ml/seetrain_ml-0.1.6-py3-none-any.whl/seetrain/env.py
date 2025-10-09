#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import enum


def get_env(key: str, default: str = None) -> str:
    return os.getenv(key, default)


class Env(enum.Enum):
    BaseURL = get_env("BASE_URL", "http://localhost:8088/api/v1")
    TaskID = get_env("TASK_ID", "0")
    Project = get_env("PROJECT", "default")
    ViewURL = get_env("VIEW_URL", "http://localhost:5173/")
