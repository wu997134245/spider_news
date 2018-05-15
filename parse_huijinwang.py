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
import os
from log import parse_log


today_date =  datetime.datetime.now().date().strftime('%Y%m%d')
current_path = os.path.dirname(os.path.realpath(__file__))






url_base = 'http://www.gold678.com'




headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.9',
'Cache-Control':'no-cache',
'Connection':'keep-alive',
'Cookie': 'Hm_lvt_61f6a0d3e85f4a965bba3c9ef59b779f=1523178575,1523338468,1523501367; UM_distinctid=162b7d85575197-0cbbc5726796c9-444a012d-144000-162b7d8557677e; CNZZDATA1258122318=484905860-1523499213-http%253A%252F%252Fwww.gold678.com%252F%7C1523499213; _ga=GA1.2.183023106.1523504135; _gid=GA1.2.2004477208.1523504135; Hm_lpvt_61f6a0d3e85f4a965bba3c9ef59b779f=1523504471',
'Host':'www.gold678.com',
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
    html = get_data(url)
    soup = BeautifulSoup(html, "html.parser")
    td = soup.find_all('div',class_ = 'overview bg-white mb20 clearfix')
    nav =  td[0]
    li = nav.find_all('li')
    parse_log.debug( li)
    a = []
    nav_url = []
    for i in li:
        a.append(i.find('a'))
    parse_log.debug( nav_url)
    filter_list = [u'黄金答疑', u'现货黄金', u'黄金T+D', u'纸黄金', u'现货白银', u'白银T+D', u'实物黄金',u'铂-银-钯']
    for i in a:
        if i.text in filter_list:
            continue
        parse_log.debug( 'u\'' + i.text + '\''+ ':' + '\'\'' + ',')
        nav_url.append({'type_name':i.text,'type_url':url_base + i['href']})

    parse_log.debug( nav_url)
    return nav_url



def get_page(url):
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
            wenzhang_url = url_base + '/C/' + wenzhang_url
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


    parse_log.debug( article_list)
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


    parse_log.debug( article_list)
    return len(article_list),article_list





def handle_article(url):
    #处理文章内容,提取标题和正文
    #处理广告,跳转链接
    html = get_data(url)
    soup = BeautifulSoup(html, "html.parser").find('div',class_='fl news_main')

    try:
        article_title = soup.find_all('h1')[0].text
    except:
        article_title=''

    try:
        artibody = soup.find_all('div',class_='news_inter_area')[0]
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

    #parse_log.info( article_title,artibody
    return article_title,artibody


def handle_hjbk_article(url):
    #处理文章内容,提取标题和正文
    #处理广告,跳转链接
    html = get_data(url)
    soup = BeautifulSoup(html, "html.parser").find('div',class_='news_inter_left')

    try:
        article_title = soup.find_all('div',class_='news_inter_title')[0].text
    except:
        article_title=''

    try:
        artibody = soup.find_all('div',class_='news_inter_area')[0]
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
    #parse_log.info( article_title, artibody
    return article_title,artibody


handle_article_CMDs={
u'黄金资讯':handle_article,
u'交易策略':handle_article,
u'黄金观察':handle_article,
u'热点局势':handle_article,
u'机构金评':handle_article,
u'深度解读':handle_article,
u'黄金博客':handle_hjbk_article,
u'铂-银-钯':handle_article,
u'原油资讯':handle_article,
u'机构评油':handle_article,
u'多空情绪':handle_article,
u'专家评油':handle_article,
u'外汇资讯':handle_article,
u'机构汇评':handle_article,
u'央行动态':handle_article,
u'专家汇评':handle_article,}






news_type = {
u'黄金资讯':'14',
u'交易策略':'4',
u'黄金观察':'4',
u'热点局势':'8',
u'机构金评':'8',
u'深度解读':'8',
u'黄金博客':'4',
u'铂-银-钯':'2',
u'原油资讯':'6',
u'机构评油':'6',
u'多空情绪':'11',
u'专家评油':'11',
u'外汇资讯':'6',
u'机构汇评':'35',
u'央行动态':'41',
u'专家汇评':'18',
}


news_type_wdgcj = {
u'黄金资讯':'54',
u'交易策略':'65',
u'黄金观察':'57',
u'热点局势':'58',
u'机构金评':'56',
u'深度解读':'59',
u'黄金博客':'55',
u'铂-银-钯':'61',
u'原油资讯':'60',
u'机构评油':'62',
u'多空情绪':'59',
u'专家评油':'57',
u'外汇资讯':'57',
u'机构汇评':'59',
u'央行动态':'60',
u'专家汇评':'59',
}




type_map = {
 "分析": "4",
 "娱乐": "11",
 "股票基金": "1",
 "入门": "35",
 "综述": "14",
 "科技中心": "38",
 "档案": "31",
 "生活": "40",
 "银行保险": "16",
 "政策": "17",
 "快讯": "10",
 "精选": "8",
 "最新": "41",
 "期货": "53",
 "排名": "33",
 "要闻": "3",
 "数据": "13",
 "市场": "6",
 "商业": "24",
 "网贷理财": "29",
 "数码": "39",
 "舆情": "34",
 "投资": "25",
 "房产": "26",
 "活动": "32",
 "理财知识": "23",
 "热点推荐": "54",
 "案例": "19",
 "新闻": "9",
 "平台": "30",
 "汽车": "27",
 "互联网": "42",
 "讲解": "12",
 "新闻热点": "7",
 "动态": "2",
 "指南": "18"
}


def get_all_article():

    article = []
    nav_url = find_data(url_base)
    article_num = 0
    article_list = []
    # nav_url.append(url_base)
    parse_log.info( '开始爬取当日所有文章链接....')
    for i in nav_url:
        # 遍历导航栏链接
        if i['type_name'] == u'黄金博客':
            page_num, art_list = get_hjbk_page(i['type_url'])
        else:
            page_num, art_list = get_page(i['type_url'])
        if not page_num:
            # 去除没有文章的分类
            continue
        parse_log.debug( u'已获取{1}文章链接{0}条'.format(page_num, i['type_name']))
        article_list.append({'type_name': i['type_name'], 'art_list': art_list})

    total = 0
    upload_end = []

    for i in article_list:
        #upload_type = news_type[i['type_name']]
        waiting_upload = i['art_list']
        parse_log.debug( '开始上传,待上传{0}条'.format(len(waiting_upload)))
        total = total + len(waiting_upload)

        for a in waiting_upload:
            if a not in upload_end:
                article_title, artibody = handle_article_CMDs[i['type_name']](a)
                if not artibody or not article_title:
                    continue
                article.append({'title':article_title,'body':artibody,'type':i['type_name'],'url':a,'source_url':url_base})
                parse_log.debug( u'正在上传:{0} 栏目.....{1}/{2}.........{3}'.format(i['type_name'], waiting_upload.index(a),
                                                                        len(waiting_upload), a))
                upload_end.append(a)
            else:
                parse_log.debug( '已存在')
                continue

    parse_log.info('已获取文章{0}条'.format(len(article)))
    return article




if __name__ == '__main__':
    pass