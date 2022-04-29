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
from collections import namedtuple

from openpyxl import load_workbook

from main import main
wb = load_workbook('source/spider_目标网站.xlsx')


data_list = [
    ('江山市塘源口莹石矿（普通合伙）', 'https://www.qcc.com/firm/4b0e6610ebb188e84964011f79590081.html'),
]

for i in data_list:
    website = Websites._make(i)

    a = main(website_name=website.name, website_url=website.url)
    # b = main2(website_name=website.name,website_url=website.url)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(a))
