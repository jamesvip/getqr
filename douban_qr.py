#! /usr/bin/env python
#! encoding:utf-8
__author__ = "James.Zhang"
# import re
import requests
import os
# from os.path import getsize,join
import sys
import logging
from bs4 import BeautifulSoup
import qrtools
import random,time
from selenium import webdriver
import selenium.webdriver.support.ui as ui
import string
import datetime
from fake_useragent import UserAgent
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import grequests
import uuid
import re

folder = "/Users/James/Documents/project/qr/img/douban/"
bakfolder = "/Users/James/Documents/project/qr/img/bak/"
url1 = "https://www.douban.com/group/search?"
url2 = "&cat=1013&q=%E7%BE%A4&sort=time"
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
            qr = qrtools.QR()
            qr.decode(filename)
            qrs.append(qr.data)


initqrs(bakfolder,1)


#headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
ua=UserAgent()
headers={"User-Agent":ua.random ,"referer":'https://www.douban.com/group', "Cookie": "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))}

os.chdir(r'/Users/James/Documents/project/qr/')
url = 'https://www.baidu.com'
fp = open('proxy.txt','r')
ips = fp.readlines()
proxys = list()
for p in ips:
    ip =p.strip('\n').split('\t')
    proxy = 'http:\\' +  ip[0] + ':' + ip[1]
    proxies = {'proxy':proxy}
    proxys.append(proxies)

def download(imgurl,tm):
    imgsrc = imgurl['src']
    lr = imgsrc[::-1]
    tms = tm.strftime('%Y-%m-%d-%H-%M-%S')
    b = tms + '_' +lr[:lr.find('/')][::-1]
    #uuid_s = str(uuid.uuid4())
    #b = 'douban_%s.jpg' % uuid_s
    img = requests.get(imgsrc, headers=headers, proxies=random.choice(proxys),timeout=(10, 30))
    with open(folder + b, 'ab') as f:
        f.write(img.content)
        f.close()
    qr = qrtools.QR()
    qr.decode(folder + b)
    #qrr = qr.data[::-1]
    if qr.data in qrs:
        print(qr.data + ' duplicate ' + imgsrc)
        os.remove(folder + b)
    elif re.search(r'https://weixin.qq.com/g/.*?',qr.data):
        qrs.append(qr.data)
        print(qr.data + ' saved weixin group ' + imgsrc)
    # elif re.search(r'http://qm.qq.com/cgi-bin/qm/qr\?k=.*?',qr.data):
    #     qrs.append(qr.data)
    else:
        print(imgsrc + ' not QR')
        os.remove(folder + b)

def main(url):
    folder = "/Users/James/Documents/project/qr/img/douban/"
    r = requests.get(url,headers = headers,proxies=random.choice(proxys))
    soup = BeautifulSoup(r.content,'lxml')
    items = soup.find_all("tr", class_="pl")
    # print items

    for item in items:
        tms = item.find_all("td", class_="td-time")[0]['title']
        suburl = item.find_all("td", class_="td-subject")[0].find_all('a', href=True)[0]['href']
        tm = datetime.datetime(*(time.strptime(tms, '%Y-%m-%d %H:%M:%S')[:6]))
        tmpoint = datetime.datetime.now() - datetime.timedelta(days = 0.5)
        if tm > tmpoint:
            sr = requests.get(suburl,headers = headers,proxies=random.choice(proxys))
            soup = BeautifulSoup(sr.content,'lxml')
            try:
                imgurls = soup.find('div', {'class': 'topic-content'}).find_all('img')
            except:
                continue
            for imgurl in imgurls:
                try:
                    download(imgurl,tm)
                except:
                    continue
            # rds = (grequests.get(imgurl['src'],headers = headers,proxies=random.choice(proxys)) for imgurl in imgurls)
            # for rd in grequests.map(rds):
            #     download(rd)
                time.sleep(1)
            time.sleep(1)
        else:
            return 1
            break

    return 0

time1 = time.time()
i = 0
while i <= 10:
   url = url1+"start="+str(50*i)+url2
   print(i)
   ret = main(url)
   if ret == 1:
       print("times up")
       break;
   i = i + 1
   time.sleep(random.randint(0, 3))
time2 = time.time()
print(u'串行耗时：' + str(time2-time1))

# urls = []
# for i in range(0, 10):
#     newpage = url1+"start="+str(50*i)+url2
#     urls.append(newpage)
# print urls
# time1 = time.time()
# tpool = ThreadPool(processes=4)
# #partial_main = partial(main, folder=folder)
# # param = {'url': urls , 'folder': folder}
# tpool.map_async(main,urls)
# tpool.close()
# tpool.join()
# time2 = time.time()
# print u'并行耗时：' + str(time2-time1)
