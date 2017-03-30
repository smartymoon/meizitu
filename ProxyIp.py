# 用于返回代理IP
import requests
class ProxyIP:
    def __init__(self, url="http://www.goubanjia.com/"):
        self.url = url

    def getIPs(self):
        return requests.get(self.url).text

if __name__ == "__main__":
    print('hello world')
