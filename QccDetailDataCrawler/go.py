# -*- coding: utf-8 -*-
"""

#
# Copyright (C) 2021 #
# @Time    : 2022/4/19 14:44
# @Author  : zicliang
# @Email   : hybpjx@163.com
# @File    : go.py
# @Software: PyCharm
"""
import asyncio
import pandas as pd

from main import main


data=pd.read_excel('source/qcc目标网站.xlsx',sheet_name='Sheet1')
name_list = list(data['name'])
url_list = list(data['url'])

for name,url in zip(name_list,url_list):
    a = main(website_name=name, website_url=url)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(a))
