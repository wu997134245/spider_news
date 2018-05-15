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
import parse_xinlang
import parse_huijinwang
import parse_wangyicaijin
import spider_rong360
import spider_south
import spider_jingjiwang
from log import parse_log
import os
from insert_mongo import *
from DBO import *

today_date = datetime.datetime.now().date().strftime('%Y-%m-%d')

current_path = os.path.dirname(os.path.realpath(__file__))


def login(username, password, login_url):
    # 登录后台
    sid = requests.session()
    sid.get(login_url)
    params = {"gotopage": "/dede/", "dopost": "login", "adminstyle": "newdedecms", "userid": username, "pwd": password,
              "sm1": ""}
    sid.post(login_url, data=params)
    return sid


def upload(article, goto):
    # 上传文章到后台
    article_title = article['title'] + goto['houzhui']
    artibody = article['body'].encode('utf8')
    try:
        upload_type = op43.query(u'''
        SELECT
            web_type_table.type_id
        FROM
            web_type_table
        WHERE
            web_type_table.type_name = ANY (
                SELECT
                    parse_id_match.destination_type_id
                FROM
                    parse_id_match
                WHERE
                    parse_id_match.source = '{0}'
                AND parse_id_match.source_type_id = '{1}'
                AND parse_id_match.destination = '{2}'
        )
    '''.format(article['source_url'], article['type'], goto['web_url']))
        upload_type = random.choice(upload_type)['type_id']

        #分类查询,分类不存在则随机生成
    except:
        upload_type = random.choice(goto['type_id'])


    this_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    params = {
        "channelid": (None, "1"),
        "dopost": (None, "save"),
        "title": (None, article_title),
        "shorttitle": (None, article_title),
        "tags": (None, article_title),
        "typeid": (None, upload_type),
        "body": (None, artibody),
        "autokey": (None, "1"),
        "ishtml": (None, "1"),
        "remote": (None, '1'),
        "pubdate": (None, this_time),
        "autolitpic": (None, '1')
    }

    sid = goto['sid']

    sid.post(goto['backend_url'], params)


def main():
    upload_goto = [
    ]
	#上传目标信息

    article_list = []
    try:
        xinlang = parse_xinlang.get_all_article()
        parse_log.info('获取新浪新闻{0}条'.format(len(xinlang)))
        article_list.extend(xinlang)
    except:
        pass

    try:
        huijinwang = parse_huijinwang.get_all_article()
        parse_log.info('获取汇金网新闻{0}条'.format(len(huijinwang)))
        article_list.extend(huijinwang)
    except:
        pass

    try:
        wangyicaijin = parse_wangyicaijin.get_all_article()
        parse_log.info('获取网易财经{0}条'.format(len(wangyicaijin)))
        article_list.extend(wangyicaijin)
    except:
        pass

    try:
        rong360 = spider_rong360.get_all_article()
        parse_log.info('获取rong360{0}条'.format(len(rong360)))
        article_list.extend(rong360)
    except:
        pass

    try:
        south_money = spider_south.get_all_article()
        parse_log.info('获取南方财富网{0}条'.format(len(south_money)))
        article_list.extend(south_money)
    except:
        pass

    try:
        jingjiwang = spider_jingjiwang.get_all_article()
        parse_log.info('获取中国经济网{0}条'.format(len(jingjiwang)))
        article_list.extend(jingjiwang)
    except:
        pass

    parse_log.info('获取文章共{0}条,开始存入数据库'.format(len(article_list)))
    for i in article_list:
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        d = {'_id': i['title'], 'title': i['title'], 'body': str(i['body']), 'type': i['type'], 'url': i['url'],
             'source_url': i['source_url'],
             'date': today_date,
             'create_time': time_now
             }
        insert_data(d, 'news_data')



    today_article = find_data({'date': today_date}, 'news_data')
    today_article = [ i for i in today_article]
    random.shuffle(today_article)
    wait_upload = []
    for i in today_article:
        wait_upload.append(i)
    parse_log.info('今日待上传{0}条'.format(len(wait_upload)))


    for i in upload_goto:
        wait_upload = wait_upload[:i['upload_max']]
        total = len(wait_upload)
        for a in wait_upload:
            upload(a, i)
        parse_log.info('上传完成{0}'.format(total))


if __name__ == '__main__':
    try:
        main()
    except:
        parse_log.exception('Exception')