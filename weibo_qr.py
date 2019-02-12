#! /usr/bin/env python
#! encoding:utf-8
__author__ = "James.Zhang"
import requests
import os
import sys
import logging
from bs4 import BeautifulSoup
import random,time
import string
import datetime
import re
from collections import deque
from fake_useragent import UserAgent
import json
import base64
#import urllib.parse
import rsa
import binascii
import os
import aiohttp
import asyncio
import aiofiles
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
from pyzbar.pyzbar import decode
from PIL import Image
from io import BytesIO
requests.adapters.DEFAULT_RETRIES = 5 # 增加重连次数
import async_timeout

imgurls = []
imgurls_qr = []
qrs = []


ua=UserAgent()
headers={"User-Agent":ua.random}
os.chdir(r'/Users/James/Documents/project/qr/')
fp = open('proxy.txt','r')
ips = fp.readlines()
proxys = list()
for p in ips:
    ip =p.strip('\n').split('\t')
    proxy =  ip[0] + ':' + ip[1]
    proxies = {'proxy':proxy}
    proxys.append(proxies)

def get_dir(url,tms):
    #tms = tm.strftime('%Y-%m-%d-%H-%M-%S')
    tms = tms.replace(' ','_')
    dir_reg = '/(\\d+)'
    reg_comp = re.compile(dir_reg)
    dirs = reg_comp.findall(url)
    #匹配失败返回一个随机数
    if len(dirs) == 0:
        return '/Users/James/Documents/project/qr/img/weibo/'+ tms + '_' + str(random.randint(100001,999999))
    return '/Users/James/Documents/project/qr/img/weibo/'+tms+ '_' + dirs[0]


headers = {
    'Host': 'm.weibo.cn',
    'Referer': 'https://m.weibo.cn/p/searchall?containerid=100103type%3D1%26q%3D%E4%BA%8C%E7%BB%B4%E7%A0%81',
    'User-Agent': UserAgent().random,
    'X-Requested-With': 'XMLHttpRequest',
}
a = 0
@asyncio.coroutine
async def get_page(url):
    global a
    try:
        # s = requests.session()
        # s.keep_alive = False  # 关闭多余连接
        #conn = aiohttp.ProxyConnector(proxy=random.choice(proxys))
        sem = asyncio.Semaphore(2)
        async with sem:
            async with aiohttp.ClientSession() as session:
                # with async_timeout.timeout(15):
                    async with session.get(url, headers=headers,timeout=10,verify_ssl=False) as r:
                        await asyncio.sleep(random.randint(1, 3))
                        if a%20 == 0:
                            await asyncio.sleep(5)
                        a = a + 1
                        print('a:' + str(a))
                        print('status:' + str(r.status))
                        if r.status == 200:
                            json = await r.json()
                            if json:
                                cards = json.get('data').get('cards')
                                for card in cards:
                                    card_groups = card.get('card_group')
                                    for card_group in card_groups:
                                        # print(card_group.get('mblog'))
                                        pics = card_group.get('mblog').get('pics')
                                        create_at = card_group.get('mblog').get('created_at')
                                        if pics != None:
                                            for pic in pics:
                                                imgs = {}
                                                imgs['url'] = pic.get('url')
                                                imgs['create_at'] = create_at
                                                if re.search(u'[\u4e00-\u9fa5]+', imgs['create_at']):
                                                    imgurls.append(imgs)
                                                    # print(imgs['url'])
                                                    # weibo.append(imgs)
                                        elif card_group['mblog'].get('retweeted_status'):
                                            # print(card_group['mblog'])
                                            pics = card_group['mblog'].get('retweeted_status').get('pics')
                                            if pics != None:
                                                for pic in pics:
                                                    imgs = {}
                                                    imgs['url'] = pic.get('url')
                                                    imgs['create_at'] = create_at
                                                    if re.search(u'[\u4e00-\u9fa5]+', imgs['create_at']):
                                                        imgurls.append(imgs)
        return r.status
    except requests.ConnectionError as e:
        print('Error', e.args)    #
    except:
        print("Unexpected error:", sys.exc_info()[0])

@asyncio.coroutine
def download(image_link):
    dir = get_dir(image_link['url'],image_link['create_at'])
    fd = dir + '.jpg'

    with open(fd, 'wb+') as f:
        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        f.write(s.get(image_link['url'], proxies=random.choice(proxys)).content)
        f.close()

@asyncio.coroutine
def decode_async(url):
    try:
        # time.sleep(random.randint(0, 1))
        s = requests.session()
        s.keep_alive = False  # 关闭多余连接
        qr = decode(Image.open(BytesIO(s.get(url['url'],proxies=random.choice(proxys)).content)))
        if qr == None or qr == []:
            print(url['url'] + ' is not QR')
        elif re.search(r'https://weixin.qq.com/g/.*?', qr[0].data.decode("utf-8")) and qr[0].data.decode("utf-8") not in qrs:
            imgurls_qr.append(url)
            qrs.append(qr[0].data.decode("utf-8"))
            print(url['url'] + ' is QR')
            dir = get_dir(url['url'], url['create_at'])
            fd = dir + '.jpg'

            with open(fd, 'wb+') as f:
                s = requests.session()
                s.keep_alive = False  # 关闭多余连接
                f.write(s.get(url['url'], proxies=random.choice(proxys)).content)
                f.close()
            return qr[0].data
    except:
        print("Unexpected error:", sys.exc_info()[0])
        pass





async def download_async(image_link):
    dir = get_dir(image_link['url'],image_link['create_at'])
    fd = dir + '.jpg'
    #print(image_link['url'])
    #conn = aiohttp.ProxyConnector(proxy=random.choice(proxys))
    async with aiohttp.ClientSession() as session:
        async with session.get(image_link['url'], headers=headers) as r:
            async with aiofiles.open(fd, 'wb') as fd:
                while True:
                    chunk = await r.content.read(1024)
                    if not chunk:
                        break
                    await fd.write(chunk)
                # print(image_link['url']+' saved weixin group ' )
            return await r.release()
            # with open(fd, 'wb+') as f:
            #     # s = requests.session()
            #     # s.keep_alive = False  # 关闭多余连接
            #     content = text.content
            #     f.write(content)
            #     f.close()


url1 = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D61%26q%3D%E6%89%AB%E7%A0%81%E8%BF%9B%E7%BE%A4%26t%3D0&page_type=searchall' #扫码进群
url2 = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D61%26q%3D%E6%89%AB%E7%A0%81%E5%8A%A0%E7%BE%A4%26t%3D0&page_type=searchall' #扫码加群
url3 = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D61%26q%3D%E7%BE%A4%E4%BA%8C%E7%BB%B4%E7%A0%81%26t%3D0&page_type=searchall' #群二维码
url4 = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D61%26q%3D%E7%BE%A4%26t%3D0&page_type=searchall'   #群
url5 = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D61%26q%3D%E5%BE%AE%E4%BF%A1%26t%3D0&page_type=searchall'   #微信
url6 = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D61%26q%3D%E4%BA%8C%E7%BB%B4%E7%A0%81%26t%3D0&page_type=searchall'    #二维码
url7 = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D61%26q%3D%E8%BF%9B%E7%BE%A4%26t%3D0&page_type=searchall'   #进群
url8 = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D61%26q%3D%E5%8A%A0%E7%BE%A4%26t%3D0&page_type=searchall'   #加群
url9 = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D61%26q%3D%E5%85%A5%E7%BE%A4%26t%3D0&page_type=searchall'   #入群

urls = []
for i in range(1, 15):
    newpage = url1+'&page='+str(i)
    urls.append(newpage)
    newpage = url2+'&page='+str(i)
    urls.append(newpage)
    newpage = url3+'&page='+str(i)
    urls.append(newpage)

for i in range(1, 100):
    newpage = url4+'&page='+str(i)
    urls.append(newpage)
    newpage = url5+'&page='+str(i)
    urls.append(newpage)
    newpage = url6+'&page='+str(i)
    urls.append(newpage)

for i in range(1, 30):
    newpage = url7+'&page='+str(i)
    urls.append(newpage)
    newpage = url8+'&page='+str(i)
    urls.append(newpage)
    newpage = url9 + '&page=' + str(i)
    urls.append(newpage)


urls_uq = list(set(urls))
urls_uq.sort(key=urls.index)








print('urls_uq:'+str(len(urls_uq)))
time1 = time.time()


loop1 = asyncio.new_event_loop()
asyncio.set_event_loop(loop1)
loop1 = asyncio.get_event_loop()

try:
    for url in urls_uq:
        task1 = asyncio.ensure_future(get_page(url))
        r = loop1.run_until_complete(task1)
        loop1.run_until_complete(asyncio.sleep(0.25))
        if r == 418:
            loop1.close()
            break
finally:
    loop1.close()

# tasks1 = [get_page(url) for url in urls_uq]
# try:
#     loop1.run_until_complete(asyncio.wait(tasks1))
# finally:
#     loop1.close()


time2 = time.time()
print(u'async get_page耗时：' + str(time2-time1))
print(len(imgurls))

loop2 = asyncio.new_event_loop()
# asyncio.set_event_loop(loop2)
tasks2 = [decode_async(url) for url in imgurls]
try:
    loop2.run_until_complete(asyncio.wait(tasks2))
    loop2.run_until_complete(asyncio.sleep(0.25))
finally:
    loop2.close()
# for url in imgurls:
#     decode_async(url)

time3 = time.time()
print(u'async decode_async耗时：' + str(time3-time2))
print(len(imgurls_qr))

# loop3 = asyncio.new_event_loop()
# # asyncio.set_event_loop(loop3)
# tasks3 = [download(image_link) for image_link in imgurls_qr]
# try:
#     loop3.run_until_complete(asyncio.wait(tasks3))
#     loop3.run_until_complete(asyncio.sleep(0.25))
# finally:
#     loop3.close()
# # for image_link in imgurls_qr:
# #     download(image_link)
#
# time4 = time.time()
# print(u'async download耗时：' + str(time4-time3))
print(u'async总耗时：' + str(time3-time1))

# time1 = time.time()
# tpool = ThreadPool(processes=4)
# tpool.map_async(main,urls_uq)
# tpool.close()
# tpool.join()
# time2 = time.time()
# print(u'并行耗时：' + str(time2-time1))