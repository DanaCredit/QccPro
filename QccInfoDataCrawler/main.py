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
import pymongo
from pyppeteer import launch
from settings.log_conf import logger

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient['QccData']
mycol = mydb['dataNews']

proxy_list = []


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
        'headless': False,  # 关闭无头模式
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
    # 也可以自定义
    await page.setViewport(viewport={"width": width, "height": height})
    # 开启js
    await page.setJavaScriptEnabled(enabled=True)
    # 设置请求头
    await page.setUserAgent(random.choice(fake_useragent.UserAgent().random))

    # 开启 隐藏 是selenium 让网站检测不到
    await page.evaluate('''() =>{ 
    Object.defineProperties(
    navigator,{ webdriver:{ get: () => false } }
    ) 
    }''')
    # 访问url
    # await page.goto(website_url, {'timeout': 10000 * 20})
    await page.goto(website_url, options={'timeout': 10000 * 30})
    await asyncio.sleep(1)

    # 滑动js  动态加载
    await page.evaluate('window.scroll(0, document.body.scrollHeight-1800)')

    await asyncio.sleep(1)

    try:
        await asyncio.sleep(3)
        content = await page.content()
        ztb = re.findall(r"(招投标 \d+)", content)[0]
        gys = re.findall(r"(供应商 \d+)", content)[0]
    except IndexError as e:
        await asyncio.sleep(1)
        await asyncio.sleep(3)
        await page.click(
            "section.bottom-nav > table > tr:nth-child(4) > td:nth-child(2) > a:nth-child(1)")
        content = await page.content()
        ztb = re.findall(r"(招投标 \d+)", content)[0]
        gys = re.findall(r"(供应商 \d+)", content)[0]

    except Exception:
        ztb = 0
        gys = 0

    mydict = {
        "网站名": website_name,
        "网站连接": website_url,
        "招投标": ztb,
        "供应商": gys,

    }
    # x = mycol.insert_one(mydict)
    mycol.update_one(mydict, {'$set': mydict}, upsert=True)

    logger.info("公司名：", website_name, "||||||", ztb, gys)
    await page.close()
    await browser.close()

# if __name__ == '__main__':
#
#     a = main()
#     loop = asyncio.get_event_loop()
#     results = loop.run_until_complete(asyncio.gather(a))
