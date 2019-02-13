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

bakfolder = "/Users/James/Documents/project/qr/img/bak/"

qrs = []
def initqrs(path,days):
    files = os.listdir(path)
    for i in files:
        filename = path + i
        if os.path.getmtime(filename) < time.time() - 3600 * 24 * days:
            try:
                if os.path.isfile(filename):
                    os.remove(filename)
                    files.remove(i)
                print("%s remove success." % filename)
            except Exception as error:
                print(error)
                print("%s remove faild." % filename)
        else:
            qr = decode(Image.open(filename))
            qrs.append(qr[0].data.decode("utf-8"))
            #print(qr[0].data.decode("utf-8"))


initqrs(bakfolder,7)


def phantomjs_getsnuid():
    from selenium import webdriver
    d=webdriver.PhantomJS('/usr/local/bin/phantomjs',service_args=['--load-images=no','--disk-cache=yes'])
    # try:
    d.get("https://www.sogou.com/web?query=")
    Snuid=d.get_cookies()[5]["value"]
    # except:
    #     Snuid=""
    d.quit()
    return Snuid



imgurls = []
imgurls_qr = []



ua=UserAgent()
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


def decode_qr(url):
    qr = decode(Image.open(BytesIO(requests.get(url).content)))
    #print(qr)
    if qr == None or qr == []:
        # print(url + ' is not QR')
        return 0
    elif re.search(r'https://weixin.qq.com/g/.*?', qr[0].data.decode("utf-8")):
        # imgurls_qr.append(url)
        # qrs.append(qr[0].data.decode("utf-8"))
        print(qr[0].data.decode("utf-8")+ ' is QR')
        return qr[0].data.decode("utf-8")

def main(url):
    headers = {
        'User-Agent': UserAgent().random
        ,'Host': 'weixin.sogou.com'
        ,'Referer': "https://weixin.sogou.com/weixin?usip=&query=%E6%89%AB%E7%A0%81%E5%8A%A0%E7%BE%A4&ft=&tsn=1&et=&interation=&type=2&wxid=&page=10&ie=utf8"
        ,'Cookie': 'CXID=A9D73D74667FAB50CD32F3E4A225659A; ad=iiidNyllll2txIu7lllllVZpuzZllllltYmDjkllll9lllllx4Dll5@@@@@@@@@@; SUID=0ABC8B715C68860A5C0699AC000107BF; IPLOC=CN6101; SUV=1546313051550944; SNUID=' + phantomjs_getsnuid() + '; LSTMV=344%2C74; LCLKINT=16334; ld=8kllllllll2t3HLRlllllVZ$TYGllllltYsjnZllll9llllllylll5@@@@@@@@@@; ABTEST=0|1546313110|v1; JSESSIONID=aaaeTSF0tGIZ2_-loa7Cw; sct=4'
    }
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    r = s.get(url, headers=headers, proxies=random.choice(proxys))
    soup = BeautifulSoup(r.content, 'html.parser')
    # print(soup)
    items = soup.find_all(lambda tag: tag.name == 'ul' and tag.get('class') == ['news-list'])[0]
    url_re = re.compile(r'http://mp.weixin.qq.com/s\?src=.*?timestamp=.*?ver=.*?signature=.*?')
    urls = []
    for a in items.find_all('a', href=True):
        if re.findall(url_re, a['href']) and a['href'] not in urls:
            urls.append(a['href'])
            # print(a['href'])
            surl = a['href']
            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            time.sleep(random.randint(0, 1))
            r = s.get(surl)
            soup = BeautifulSoup(r.content, 'html.parser')
            for item in soup.find_all(lambda tag: tag.name == 'img' and tag.get('data-type') == 'jpeg'):
                try:
                    qr = decode_qr(item['data-src'])
                except Exception as err:
                    print(err)
                    continue
                fd = '/Users/James/Documents/project/qr/img/sogou/sogou_'+str(random.randint(100001,999999))+'.jpg'
                if qr == u'' or qr == -1:
                    print(item['data-src'] + ' 解码失败')
                elif qr == 0:
                    print(item['data-src'] + ' not QR')
                elif str(qr) in qrs:
                    print(qr + ' duplicate ' + item['data-src'])
                elif re.search(r'https://weixin.qq.com/g/.*?', str(qr)):
                    with open(fd, 'wb+') as f:
                        s = requests.session()
                        s.keep_alive = False  # 关闭多余连接
                        f.write(s.get(item['data-src'], timeout=(30, 60)).content)
                    print(qr + ' saved weixin group ' + item['data-src'])
                    qrs.append(qr)

url1 = 'https://weixin.sogou.com/weixin?usip=&query=%E6%89%AB%E7%A0%81%E5%8A%A0%E7%BE%A4&ft=&tsn=1&et=&interation=&type=2&wxid=&page='  #扫码加群
url2 = 'https://weixin.sogou.com/weixin?usip=&query=%E6%89%AB%E7%A0%81%E8%BF%9B%E7%BE%A4&ft=&tsn=1&et=&interation=&type=2&wxid=&page='  #扫码进群
url3 = 'https://weixin.sogou.com/weixin?usip=&query=%E7%BE%A4%E4%BA%8C%E7%BB%B4%E7%A0%81&ft=&tsn=1&et=&interation=&type=2&wxid=&page='  #群二维码
url4 = 'https://weixin.sogou.com/weixin?usip=&query=%E8%BF%9B%E7%BE%A4&ft=&tsn=1&et=&interation=&type=2&wxid=&page=' #进群
url5 = 'https://weixin.sogou.com/weixin?usip=&query=%E5%8A%A0%E7%BE%A4&ft=&tsn=1&et=&interation=&type=2&wxid=&page=' #加群
url6 = 'https://weixin.sogou.com/weixin?usip=&query=%E5%85%A5%E7%BE%A4&ft=&tsn=1&et=&interation=&type=2&wxid=&page=' #入群

urls = []
for i in range(1, 11):
    newpage = url1+str(i)+'&ie=utf8'
    urls.append(newpage)
for i in range(1, 11):
    newpage = url2+str(i)+'&ie=utf8'
    urls.append(newpage)
for i in range(1, 11):
    newpage = url3+str(i)+'&ie=utf8'
    urls.append(newpage)
for i in range(1, 11):
    newpage = url4+str(i)+'&ie=utf8'
    urls.append(newpage)
for i in range(1, 11):
    newpage = url5+str(i)+'&ie=utf8'
    urls.append(newpage)
for i in range(1, 11):
    newpage = url6+str(i)+'&ie=utf8'
    urls.append(newpage)

urls_uq = list(set(urls))
urls_uq.sort(key=urls.index)
n = len(urls_uq)
print('urls_uq:'+str(n))

time1 = time.time()
i = 1
for url in urls_uq:
   main(url)
   print(str(i)+'/'+str(n))
   i = i + 1
   time.sleep(random.randint(0, 1))
time2 = time.time()
print(u'串行耗时：' + str(time2-time1))
print('qrs:'+str(len(qrs)))
