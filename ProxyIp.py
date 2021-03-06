# 用于返回代理IP
import requests
from pymongo import MongoClient
import json
import time

class ProxyIP:
    def __init__(self, url="http://api.goubanjia.com/api/get.shtml?order=dda6296ac277e375c32d49682c8553c0&num=100&area=%E4%B8%AD%E5%9B%BD&carrier=3&protocol=1&an1=1&an2=2&an3=3&sp1=1&sort=1&system=1&distinct=0&rettype=0&seprator=%0D%0A"):
        self.url = url
        self.db = MongoClient()["meizitu"]
        self.dbCollection = self.db['ipList']


    def getIP(self):
        record = self.dbCollection.find_one_and_update({'status':"unuse"}, {'$set':{'status':"used"}})
        if record:
            return str(record['ip']) + ":" + str(record['port'])
        else:
            self.api()
            return self.getIP()

    def api(self):
        time.sleep(1)
        try:
            ipJson = requests.get(self.url).text
            list = json.loads(ipJson)['data']
            def setUnused(dict):
                dict['status'] = 'unuse'
                return dict
            new_list = map(setUnused, list)
            self.dbCollection.insert(new_list)
        except:
            time.sleep(1)
            self.api()

if __name__ == "__main__":
    p = ProxyIP()
    for i in range(3):
        print(p.getIP())
