"""
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 #
# @Time    : 2022/4/18 14:19
# @Author  : zicliang
# @Email   : hybpjx@163.com
# @File    : log_conf.py
# @Software: PyCharm
"""
import datetime
import os
from loguru import logger

BASE_DIR = os.path.abspath(".")
file_name = os.path.join(BASE_DIR, f'log/{datetime.date.today()}.log')

log_level = "WARNING"
# feature 字符串格式化
logger.add(file_name, rotation="10 MB", enqueue=True, level=log_level,format="{time} {level} {message}")
