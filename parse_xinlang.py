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
import os
from log import parse_log



today_date =  datetime.datetime.now().date().strftime('%Y-%m-%d')
current_path = os.path.dirname(os.path.realpath(__file__))




url_base = 'http://finance.sina.com.cn/'



def get_data(url = url_base):

    headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.9',
'Cache-Control':'no-cache',
'Connection':'keep-alive',
'Cookie':'SINAGLOBAL=172.16.92.27_1502696007.918727; U_TRS1=000000df.d3d34fb6.59b1f948.d185659f; UOR=www.baidu.com,blog.sina.com.cn,; SGUID=1505963540609_62288743; FINA_V_S_2=sh000001; SUB=_2AkMtJdNKf8NxqwJRmP0WymLlZI93yA3EieKbeSKRJRMyHRl-yD83qmohtRB6BqX9pWo9afQfzpGJShIOQzoy5ommFIJW; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WF7rkwGHOQfP-POpen-JnHJ; Apache=101.81.23.48_1523178808.344731; U_TRS2=00000030.d32f5b48.5ac9dd39.80d687be; ULV=1523178811684',
'Host':'finance.sina.com.cn',
'Pragma':'no-cache',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
               }
    r = requests.get(url, headers=headers)
    return r.content


def find_data(url):
    #获取导航栏URL
    html = get_data(url)
    soup = BeautifulSoup(html, "html.parser")
    td = soup.find_all('div',class_ = 'm-nav')
    nav =  td[0]
    li = nav.find_all('a')
    nav_url = []
    for i in li:
        parse_log.debug( i)
        nav_url.append({'type_name':i.text,'type_url':i['href']})
    parse_log.debug( nav_url)
    return nav_url



def get_page(url):
    #获取文章URL链接,获取当日文章
    html = get_data(url)
    soup = BeautifulSoup(html, "html.parser")
    a = soup.find_all('a')
    article_list = []
    for i in a :
        try:
            wenzhang_url =  i['href']
            search_obj = re.search(r'http://.+?{0}.+?\.shtml'.format(today_date),wenzhang_url)
            wenzhang_filter = search_obj.group()
            #parse_log.debug( wenzhang_filter
            article_list.append(wenzhang_filter)
        except:
            continue

    return len(article_list),article_list



def save_data(num):
    pass



def handle_article(url):
    #处理文章内容,提取标题和正文
    #处理广告,跳转链接
    html = get_data(url)
    soup = BeautifulSoup(html, "html.parser")
    try:
        article_title = soup.find_all('h1',class_="main-title")[0].text
    except:
        article_title=''

    try:
        artibody = soup.find_all('div',id='artibody')[0]
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

    return article_title,artibody




news_type = {
             u'股票':'1',
             u'新股':'1',
             u'港股':'1',
             u'美股':'1',
             u'基金':'1',
             u'期货':'1',
             u'外汇':'1',
             u'黄金':'1',
             u'债券':'1',
             u'理财':'23',
             u'银行': "32",
             u'保险': "32",
             u'信托': "32",
             u'新三板': "32",
             u'专栏': "32",
             u'博客': "32",
             u'股吧': "32",
             u'会议': "32",
             u'数据': "32",
             u'直播': "32",
             u'众测': "32"
             }

news_type_wdgcj = {
             u'股票':'54',
             u'新股':'54',
             u'港股':'55',
             u'美股':'56',
             u'基金':'57',
             u'期货':'58',
             u'外汇':'59',
             u'黄金':'58',
             u'债券':'57',
             u'理财':'54',
             u'银行': "58",
             u'保险': "60",
             u'信托': "61",
             u'新三板': "62",
             u'专栏': "63",
             u'博客': "59",
             u'股吧': "60",
             u'会议': "63",
             u'数据': "64",
             u'直播': "66",
             u'众测': "65"
             }


def get_all_article():

    article = []
    nav_url = find_data(url_base)
    article_num = 0
    article_list = []
    #nav_url.append(url_base)
    parse_log.info( '开始爬取当日所有文章链接....')
    for i in nav_url:
        #遍历导航栏链接
        page_num,art_list = get_page(i['type_url'])
        if not page_num:
            #去除没有文章的分类
            continue
        parse_log.debug( '已获取文章链接{0}条'.format(page_num ))
        article_list.append({'type_name':i['type_name'],'art_list':art_list})

    upload_end = []

    total = 0


    for i in article_list:
        #upload_type = news_type[i['type_name']]
        waiting_upload = i['art_list']
        #parse_log.debug( '开始上传,待上传{0}条'.format(len(waiting_upload))
        total = total + len(waiting_upload)
        for a in waiting_upload:
            if a not in upload_end:
                article_title, artibody = handle_article(a)
                if not artibody or not article_title:
                    continue
                article.append({'title': article_title, 'body': artibody, 'type': i['type_name'], 'url': a,'source_url':url_base})

                parse_log.debug( u'获取文章内容:{0} 栏目.....{1}/{2}........{3}'.format(i['type_name'], waiting_upload.index(a),len(waiting_upload), a,))
                upload_end.append(a)

            else:
                parse_log.debug( '已存在')
                continue

    parse_log.info('已获取文章{0}条'.format(len(article)))
    return article









if __name__ == '__main__':
    pass