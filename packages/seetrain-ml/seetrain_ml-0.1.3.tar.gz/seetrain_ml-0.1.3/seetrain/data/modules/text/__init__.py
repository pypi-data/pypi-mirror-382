#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Union

class Text:
    def __init__(self, data: str):
        self.data = data
    
    def get_data(self):
        return self.data