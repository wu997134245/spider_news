# coding=utf-8
import subprocess
from pymongo import MongoClient
import time
import ConfigParser
import os
current_path = os.path.dirname(os.path.realpath(__file__))


configfile = os.path.join(current_path,'config.ini')
source = 'operation'
cf = ConfigParser.ConfigParser()
cf.read(configfile)
host = cf.get(source,'host')
port = int(cf.get(source,'port'))
user = cf.get(source,'user')
passwd = cf.get(source,'passwd')
db = cf.get(source,'db')
collection = cf.get(source,'collection')


client = MongoClient(host, port)
dbc = client.get_database(db)
dbc.authenticate(user, passwd)


def insert_data(data,table):
    table = dbc.get_collection(table)
    table.save(data)
    client.close()


def find_data(condition,table):
    table = dbc.get_collection(table)
    data = table.find(condition)
    client.close()
    return data


def update_data(where_data,data,table):
    client = MongoClient(host, port)
    dbc = client.get_database(db)
    dbc.authenticate(user, passwd)
    table = dbc.get_collection(table)
    table.update(where_data,{'$set':data})
    client.close()