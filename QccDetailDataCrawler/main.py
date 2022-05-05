"""
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 #
# @Time    : 2022/4/19 14:43
# @Author  : zicliang
# @Email   : hybpjx@163.com
# @File    : main.py
# @Software: PyCharm
"""
import asyncio
import random
import re
import fake_useragent
import pandas as pd

from openpyxl import load_workbook
from pyquery import PyQuery as pq
from pyppeteer import launch

from pymongo import MongoClient

# 得到一个连接对象
client = MongoClient("mongodb://localhost:27017/")
# 先删除 UrlStatus 数据库
client.drop_database("QccUrlNumber")
# 再创建 UrlStatus 数据库
db = client.QccUrlNumber
# 创建 status 集合
coll = db.status


def screen_size():
    """使用tkinter获取屏幕大小"""
    # 导入gui编程的模块
    import tkinter
    # 创建一个空间界面
    tk = tkinter.Tk()
    # 获得宽高
    width = tk.winfo_screenwidth()
    height = tk.winfo_screenheight()
    tk.quit()
    # 得到返回值
    return width, height


async def main(website_name, website_url):

    # 默认无头浏览器  沙盒模式
    browser = await launch({
        'headless': True,  # 关闭无头模式
        'devtools': True,  # 控制界面的显示，用来调试
        'executablePath': '',
        'args': [
            '--disable-extensions',
            '--hide-scrollbars',
            '--disable-bundled-ppapi-flash',
            '--mute-audio',
            '--no-sandbox',  # --no-sandbox 在 docker 里使用时需要加入的参数，不然会报错
            '--disable-gpu',
            '--disable-xss-auditor',
            # 页面全屏
            '--start-maximized',
            # '--proxy-server=117.94.222.196'
        ],
        # 忽略自动化控制
        'ignoreDefaultArgs': ['--enable-automation'],
        'dumpio': True,  # 解决浏览器多开卡死
    })
    # 新开一个page对象
    page = await browser.newPage()

    # 拿到一个尺寸 作为你的谷歌浏览器大小
    width, height = screen_size()

    tasks = [
        # 设置UA
        asyncio.ensure_future(page.setUserAgent(random.choice(fake_useragent.UserAgent().random))),
        # 启用JS，不开的话无法执行JS
        asyncio.ensure_future(page.setJavaScriptEnabled(True)),
        # 关闭缓存
        asyncio.ensure_future(page.setCacheEnabled(False)),
        # 设置窗口大小
        asyncio.ensure_future(page.setViewport({"width": width, "height": height}))
    ]
    await asyncio.wait(tasks)
    # 开启 隐藏 是selenium 让网站检测不到
    await page.evaluate('''() =>{ 
    Object.defineProperties(
    navigator,{ webdriver:{ get: () => false } }
    ) 
    }''')

    # cookies = eval(open("cookies/cookie.txt", 'r', encoding="utf-8").read())

    # await page.setCookie()

    await asyncio.sleep(15)
    # 访问url
    await page.goto(website_url, {'timeout': 10000 * 20})
    await asyncio.sleep(1)

    # 滑动js  动态加载
    await page.evaluate('window.scroll(0, document.body.scrollHeight)')

    await asyncio.sleep(1)

    page_soucre = await page.content()

    doc = pq(page_soucre)

    info_website = pd.DataFrame(
        {
            '公司名': [website_name],
            '公司qcc链接地址': [website_url],
            '招投标': [doc('.item:contains(招投标)').text()],
            '供应商': [doc('.item:contains(供应商)').text()],
            '竞争对手': [doc('.item:contains(竞争对手)').text()],
            '新闻舆情': [doc('.item:contains(新闻舆情)').text()],
            '微信公众号': [doc('.item:contains(微信公众号)').text()],
            '相关公告': [doc('.item:contains(相关公告)').text()],
        }
    )
    writer = pd.ExcelWriter('source/website.xlsx')

    info_website.to_excel(writer)
    writer.save()
    print(info_website)

    mydict = {
            '公司名': [website_name],
            '公司qcc链接地址': [website_url],
            '招投标': [doc('.item:contains(招投标)').text()],
            '供应商': [doc('.item:contains(供应商)').text()],
            '竞争对手': [doc('.item:contains(竞争对手)').text()],
            '新闻舆情': [doc('.item:contains(新闻舆情)').text()],
            '微信公众号': [doc('.item:contains(微信公众号)').text()],
            '相关公告': [doc('.item:contains(相关公告)').text()],
        }
    coll.update_one(mydict, {'$set': mydict}, upsert=True)

    await page.close()
    await browser.close()


if __name__ == '__main__':
    cookies = eval(open("cookies/cookie.txt", 'r', encoding="utf-8").read())
    print(random.choice(cookies))
