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
import re
from collections import deque
from fake_useragent import UserAgent
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import json
requests.adapters.DEFAULT_RETRIES = 5 # 增加重连次数
from pyzbar.pyzbar import decode
from PIL import Image
from io import BytesIO


#link_queue = deque()
total_page = 16
page_size = 0
#headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
ua=UserAgent()
headers={"User-Agent":ua.random}

url1 = 'http://tieba.baidu.com/f/search/res?ie=utf-8&qw=%E6%89%AB%E7%A0%81%E8%BF%9B%E7%BE%A4' #扫码进群
url2 = 'http://tieba.baidu.com/f/search/res?ie=utf-8&qw=%E6%89%AB%E7%A0%81%E5%8A%A0%E7%BE%A4' #扫码加群
url3 = 'http://tieba.baidu.com/f/search/res?ie=utf-8&qw=%E7%BE%A4%E4%BA%8C%E7%BB%B4%E7%A0%81' #群二维码
url4 = 'http://tieba.baidu.com/f/search/res?ie=utf-8&qw=%E7%BE%A4' #群
url5 = 'http://tieba.baidu.com/f/search/res?ie=utf-8&qw=%E4%BA%8C%E7%BB%B4%E7%A0%81' #二维码
url6 = 'http://tieba.baidu.com/f/search/res?ie=utf-8&qw=%E5%BE%AE%E4%BF%A1' #微信
url7 = 'http://tieba.baidu.com/f/search/res?ie=utf-8&qw=%E8%BF%9B%E7%BE%A4' #进群
url8 = 'http://tieba.baidu.com/f/search/res?ie=utf-8&qw=%E5%8A%A0%E7%BE%A4' #加群

qrs = []
os.chdir(r'/Users/James/Documents/project/qr/')
fp = open('proxy.txt','r')
ips = fp.readlines()
proxys = list()
for p in ips:
    ip =p.strip('\n').split('\t')
    proxy = 'http:\\' +  ip[0] + ':' + ip[1]
    proxies = {'proxy':proxy}
    proxys.append(proxies)


def has_next_page(data):
    reg = 'pn=(.*)?">下一页'
    reg_comp = re.compile(reg)
    return not len(reg_comp.findall(data)) == 0

def get_dir(url,tm):
    tms = tm.strftime('%Y-%m-%d-%H-%M-%S')
    dir_reg = '/(\\d+)'
    reg_comp = re.compile(dir_reg)
    dirs = reg_comp.findall(url)
    #匹配失败返回一个随机数
    if len(dirs) == 0:
        return '/Users/James/Documents/project/qr/img/tieba/'+ tms + '_' + random.randint()
    return '/Users/James/Documents/project/qr/img/tieba/'+tms+ '_' + dirs[0]


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


qrs = []
def main(url):
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    r = s.get(url,headers = headers,proxies=random.choice(proxys),timeout=(30, 60))
    soup = BeautifulSoup(r.content, 'html.parser')
        # data = url_open.read().decode('utf-8')
    items = soup.find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['s_post'])
    for item in items:
        try:
            tms = item.find('font',class_="p_green p_date").text
            title = item.find('span',class_="p_title").find('a').text
            # print(title)
        except Exception as err:
            print(item)
            print(err)
            continue
        tm = datetime.datetime(*(time.strptime(tms, '%Y-%m-%d %H:%M')[:6]))
        tmpoint = datetime.datetime.now() - datetime.timedelta(days = 0.6)
        if tm > tmpoint and title.find('回复') == -1:
            print(title)
            link = re.compile('href=\"(/p/.+?)\"').findall(str(item))[0]
            detail_link = 'https://tieba.baidu.com' + link
            #link_queue.append(detail_link)
            #print('detail_link:' + detail_link)
            dir = get_dir(detail_link,tm)
            #print dir
            pn = 1
            while pn < 5:
                print(pn)
                if '?' in detail_link:
                    # 地址中已经有了参数
                    full_detail_link = detail_link + '&pn=%d' % pn
                else:
                    # 地址中尚未有参数
                    full_detail_link = detail_link + '?pn=%d' % pn
                #print('full_detail_link:' + full_detail_link)
                s = requests.session()
                s.keep_alive = False  # 关闭多余连接
                try:
                    detail_data = s.get(full_detail_link,headers = headers,proxies=random.choice(proxys), timeout=(30, 60)).text
                except Exception as err:
                    print(err)
                    continue
                image_re = re.compile(r'https?://img.*?/sign=.*?.jpg')
                all_image_links = re.findall(image_re, detail_data)
                #print all_image_links
                pic_total = 0
                for image_link in all_image_links:
                    #time.sleep(0.01)
                    try:
                        qr = decode_qr(image_link)
                    except Exception as err:
                        print(err)
                        continue
                    fd = dir + '_%d.jpg' % pic_total
                    if qr == u'' or qr == -1:
                        print(image_link + ' 解码失败')
                    elif qr == 0:
                        print(image_link + ' not QR')
                    elif str(qr) in qrs:
                        print(qr + ' duplicate '+image_link)
                    elif re.search(r'https://weixin.qq.com/g/.*?',str(qr)):
                        with open(fd, 'wb+') as f:
                            s = requests.session()
                            s.keep_alive = False  # 关闭多余连接
                            f.write(s.get(image_link, headers=headers, proxies=random.choice(proxys),timeout=(30, 60)).content)
                        print(qr + ' saved weixin group ' + image_link)
                        qrs.append(qr)
                    # elif re.search(r'http://qm.qq.com/cgi-bin/qm/qr\?k=.*?',qr):
                    #     with open(fd, 'wb+') as f:
                    #         f.write(requests.get(image_link, headers=headers, proxies=random.choice(proxys)).content)
                    #     print(qr + ' saved qq group ' + image_link)
                    #     qrs.append(qr)
                        #print(qr + ' saved '+fd)
                    # pic_total += 1
                if not has_next_page(detail_data):
                    break
                pn += 1
        #else:
         #   continue
    return 0
    #page_size = len(all_linkers)


urls = []
for i in range(1, 15):
    newpage = url1+'&pn='+str(i)
    urls.append(newpage)
for i in range(1, 15):
    newpage = url2+'&pn='+str(i)
    urls.append(newpage)
for i in range(1, 15):
    newpage = url3+'&pn='+str(i)
    urls.append(newpage)
for i in range(1, 15):
    newpage = url4+'&pn='+str(i)
    urls.append(newpage)
for i in range(1, 15): #群
    newpage = url5+'&pn='+str(i)
    urls.append(newpage)
for i in range(1, 15):
    newpage = url6+'&pn='+str(i)
    urls.append(newpage)
for i in range(1, 10): #群
    newpage = url7+'&pn='+str(i)
    urls.append(newpage)
for i in range(1, 10):
    newpage = url8+'&pn='+str(i)
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



# time1 = time.time()
# tpool = ThreadPool(processes=2)
# tpool.map_async(main,urls_uq)
# tpool.close()
# tpool.join()
# time2 = time.time()
# print u'并行耗时：' + str(time2-time1)
