# coding=utf-8
import random

import requests
import time
from bs4 import BeautifulSoup
import random
import re
import time
import datetime
import requests
import json
import cPickle as p
from log import parse_log
import os
from multiprocessing.dummy import Pool as ThreadPool




current_path = os.path.dirname(os.path.realpath(__file__))
today_date =  datetime.datetime.now().date().strftime('%Y-%m-%d')





url_base = 'http://www.southmoney.com/'





headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.9',
'Cache-Control':'no-cache',
'Connection':'keep-alive',
'Host':'www.southmoney.com',
'Pragma':'no-cache',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
               }


def get_data(url = url_base):
    r = requests.get(url, headers=headers)
    return r.content



def post_data(url,params):
    r = requests.post(url, headers=headers,params=params)
    return r.content




def find_data(url):
    #获取导航栏URL
    try:
        html = get_data(url).decode('gbk').encode('utf8')
    except:
        html = get_data(url)
    nav_url = []
    soup = BeautifulSoup(html, "html.parser")
    nav = soup.find('div',class_='nav')
    a = nav.find_all('a')

    for i in a:
        try:
            wenzhang_url = i['href']
            type_name = i.text
        except:
            continue
        nav_url.append({'type_name': type_name, 'type_url': wenzhang_url})



    return nav_url



def get_page(url,type_name):

    def get_next_page(next_page_url,article_list,num,type_name):
        html = get_data(next_page_url)
        soup = BeautifulSoup(html, "html.parser")
        a = soup.find_all(name='a', href=re.compile('.+?2018.+?.html'))
        if num == 2:
            return article_list


        for i in a:
            try:
                wenzhang_url = i['href']
                wenzhang_url = 'http://www.southmoney.com' + wenzhang_url
                article_list.append({'wenzhang_url':wenzhang_url,'type_name':type_name})
            except:
                continue
        try:
            next_page_url = url + soup.find('a', text='下一页')['href']
        except:
            return article_list

        num += 1
        return get_next_page(next_page_url,article_list,num,type_name)

    article_list = get_next_page(url,[],0,type_name)

    return len(article_list),article_list






def handle_article(url):
    #处理文章内容,提取标题和正文
    #处理广告,跳转链接
    #print url
    try:
        html = get_data(url).decode('gbk').encode('utf8')
    except:
        try:
            html = get_data(url)
        except:
            return '',''

    soup = BeautifulSoup(html, "html.parser").find('div',class_='article')

    try:
        article_title = soup.find('h1',class_='artTitle').text
    except:
        article_title=''

    try:
        artDate = soup.find('p',class_='artDate').text
        re.search(today_date,artDate).group()
    except:
        return '',''

    try:
        artibody = soup.find('div',class_='articleCon')
    except:
        artibody=''

    try:
        advertising = soup.find_all('div',class_='hqimg_related')[0]
        advertising.extract()
    except:
        pass

    try:
        a_tag = soup.find_all('a')
        for i in a_tag:
            del i['href']
    except:
        pass

    #parse_log.debug() article_title,artibody
    return article_title,artibody


class Cache_file:
    def __init__(self):
        self.file_name = 'cache_file.txt'
        if not os.path.isfile(self.file_name):
            with open(self.file_name,'w') as f:
                p.dump([],f)


    def read(self):
        f = open(self.file_name)
        data = p.load(f)
        f.close()
        return data


    def save(self,data):
        f = open(self.file_name,'w')
        p.dump(data,f)
        f.close()


def get_all_article():

    article = []
    nav_url = find_data(url_base)
    article_num = 0
    article_list = []
    # nav_url.append(url_base)
    parse_log.info('开始爬取当日所有文章链接....')
    for i in nav_url:
        #遍历导航栏链接
        page_num, art_list = get_page(i['type_url'],i['type_name'])
        if not page_num:
            #去除没有文章的分类
            continue
        article_list.extend(art_list)

    parse_log.info('已获取链接{0}条'.format(len(article_list)))
    cache = Cache_file()
    url_list = cache.read()



    total = 0
    upload_end = []

    def get_wenzhang(i):
        if i['wenzhang_url'] in url_list:
            return
        article_title, artibody = handle_article(i['wenzhang_url'])
        url_list.append(i['wenzhang_url'])
        if not artibody or not article_title:
            return
        return {'title': article_title, 'body': artibody, 'type': i['type_name'], 'url':i['wenzhang_url'],'source_url':url_base}



    pool = ThreadPool(4)
    results = pool.map(get_wenzhang, article_list)
    pool.close()
    pool.join()
    results2 = []
    for i in results:
        if i is None:
            continue
        results2.append(i)

    cache.save(url_list)
    #parse_log.info('已获取文章{0}条'.format(len(results2)))
    return results2






if __name__ == '__main__':
    get_all_article()
    #handle_article(url_wenzhang)
    #upload()
