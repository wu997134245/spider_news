import dbpools
import os
current_path = os.path.dirname(os.path.realpath(__file__))


configfile = os.path.join(current_path,'config.ini')
source = 'new_operations'
cf = ConfigParser.ConfigParser()
cf.read(configfile)
host = cf.get(source,'host')
port = int(cf.get(source,'port'))
user = cf.get(source,'user')
passwd = cf.get(source,'passwd')
db = cf.get(source,'db')


host
database
user
password




op43 = dbpools.Connection(host=host, database=db,user=user, password=passwd, charset='utf8')

