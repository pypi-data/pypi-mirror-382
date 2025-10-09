# -*- coding: utf-8 -*-
# Author: chenxi7310@cvte.com
# Date: 2023-12-27
# Desc:

import json
import requests


class BuildRequest:
    def __init__(self, headers: dict):
        self.headers = headers
        # 可由外部注入会话（带重试/连接复用）
        self.session = None

    def _response(self, res: requests.Response) -> any:
        if res.status_code != 200:
            raise Exception(f'status_code:{res.status_code}')
        body = json.loads(res.text)
        status = body.get("status", -1)
        msg = body.get("msg", None)
        data = body.get("data", None)
        if status != 0:
            raise Exception(f'status:{status} msg:{msg}')
        return data

    def get(self, url: str):
        sess = self.session or requests
        res = sess.get(url=url, headers=self.headers)
        return self._response(res=res)

    def post(self, url: str, body: dict):
        sess = self.session or requests
        res = sess.post(url=url, json=body, headers=self.headers)
        return self._response(res=res)

    def put(self, url: str, body: dict):
        sess = self.session or requests
        res = sess.put(url=url, json=body, headers=self.headers)
        return self._response(res=res)

    def delete(self, url: str, body: dict):
        sess = self.session or requests
        res = sess.delete(url=url, json=body, headers=self.headers)
        return self._response(res=res)

    def upload(self, url: str, filename: str, file: bytes, file_type: str, task_id: str = ""):
        files = [
            ("file", (filename, file, file_type))
        ]
        data = {
            "file_type": file_type,
            "task_id": task_id
        }
        # 移除Content-Type头部，让requests自动设置multipart/form-data
        headers = {k: v for k, v in self.headers.items() if k.lower() != 'content-type'}
        sess = self.session or requests
        res = sess.post(url=url, data=data, files=files, headers=headers)
        return self._response(res=res)
