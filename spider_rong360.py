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

current_path = os.path.dirname(os.path.realpath(__file__))
today_date =  datetime.datetime.now().date().strftime('/%Y/%m/%d/')





url_base = 'https://www.rong360.com/licai/'





headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.9',
'Cache-Control':'no-cache',
'Connection':'keep-alive',
'Host':'www.rong360.com',
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
    nav_url = []
    html = get_data(url)
    soup = BeautifulSoup(html, "html.parser")
    h2 = soup.find_all('h2')
    for i in h2:
        try:
            wenzhang_url = i.find('a')['href']
        except:
            continue
        search_obj = re.search(r'.+licai-news.+'.format(today_date), wenzhang_url)
        if not search_obj:
            continue
        type_name = i.find('b').text
        nav_url.append({'type_name': type_name, 'type_url': wenzhang_url})
    parse_log.debug(nav_url)
    nav_url.append({'type_name':u'要闻','type_url':u'https://www.rong360.com/licai-news/?typeid=151'})


    return nav_url



def get_page(url):
    #获取文章URL链接,获取当日文章
    next_page_url = url
    art_list = []

    def get_rules_page_1(art_list, next_page_url):
        try:
            html = get_data(next_page_url)
        except:
            return art_list
        soup = BeautifulSoup(html, "html.parser")
        div_list = soup.find('div',class_='list_content_l')
        next_page_url = 'https://www.rong360.com' + soup.find('a',text=u'下一页')['href']
        p = div_list.find_all('p', class_ ='s_tit')
        a = []
        num = len(art_list)
        for i in p:
            a.append(i.find('a'))
        for i in a:
            try:
                wenzhang_url = i['href']
                search_obj = re.search(r'.+{0}.+?html'.format(today_date), wenzhang_url)
                search_obj.group()
            except:
                continue
            art_list.append(wenzhang_url)
        if len(art_list) == num:
            return art_list

        get_rules_page_1(art_list,next_page_url)
        return art_list, next_page_url

    article_list = get_rules_page_1(art_list,next_page_url)
    parse_log.debug(article_list)

    return len(article_list),article_list







def get_hjbk_page(url):
    #获取文章URL链接,获取当日文章
    column_url = url + '/page'
    page_num = 1
    article_list = []

    def get_url(page_num):
        html = json.loads(post_data(column_url,{'page':page_num}))['data']
        added_url = 0
        for i in html:
            try:
                wenzhang_url = i['NewsID']
            except:
                continue
            search_obj = re.search(r'{0}.+?'.format(today_date), wenzhang_url)
            if not search_obj:
                continue
            wenzhang_url = url_base + '/C/' + wenzhang_url[:8] + "/" + wenzhang_url + ".html"
            article_list.append(wenzhang_url)
            added_url +=1

        if added_url == len(html):
            return 1
        else:
            return 0


    while True:
        status = get_url(page_num)
        if status:
            page_num+=1
        else:
            break
    parse_log.debug(article_list)
    return len(article_list),article_list





def handle_article(url):
    #处理文章内容,提取标题和正文
    #处理广告,跳转链接
    try:
        html = get_data(url).decode('gbk').encode('utf8')
    except:
        html = get_data(url)
    soup = BeautifulSoup(html, "html.parser").find('div',class_='dcl_box')

    try:
        article_title = soup.find_all('h1')[0].text
    except:
        article_title=''

    try:
        artibody = soup.find_all('div',class_='txt')[0]
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



def get_all_article():

    article = []
    nav_url = find_data(url_base)
    article_num = 0
    article_list = []
    # nav_url.append(url_base)
    parse_log.info('开始爬取当日所有文章链接....')
    for i in nav_url:
        #遍历导航栏链接
        #page_num, art_list = get_article_CMDs[i['type_name']](i['type_url'])
        page_num, art_list = get_page(i['type_url'])
        if not page_num:
            #去除没有文章的分类
            continue
        parse_log.debug(u'已获取{1}文章链接{0}条'.format(page_num,i['type_name'] ))
        article_list.append({'type_name':i['type_name'],'art_list':art_list})




    total = 0
    upload_end = []

    for i in article_list:
        #upload_type = news_type[i['type_name']]
        waiting_upload = i['art_list'][0]
        parse_log.debug('开始上传,待上传{0}条'.format(len(waiting_upload)))
        total = total + len(waiting_upload)

        for a in waiting_upload:
            if a not in upload_end:
                article_title, artibody = handle_article(a)
                time.sleep(0.2)
                if not artibody or not article_title:
                    continue
                article.append({'title': article_title, 'body': artibody, 'type': i['type_name'], 'url': a,'source_url': url_base})
                parse_log.debug(u'获取文章:{0} 栏目.....{1}/{2}.........{3}'.format(i['type_name'], waiting_upload.index(a),
                                                                        len(waiting_upload), a))
                upload_end.append(a)
            else:
                parse_log.debug('已存在')
                continue
    parse_log.info('已获取文章{0}条'.format(len(article)))
    return article






if __name__ == '__main__':
    get_all_article()
    #handle_article(url_wenzhang)
    #upload()