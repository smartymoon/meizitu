import datetime
import time
from multiprocessing import Pool
import random
import requests
from bs4 import BeautifulSoup
import ProxyIp
import os
from pymongo import MongoClient

class download:
    rootDir = 'D:\mzitu'
    timeOut = 2
    tryTimes = 3  # ip 失败后试３次
    limitTimes = 3
    agents = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]
    def __init__(self):
        self.makeDir(self.rootDir)
        # init mongodb
        self.database = MongoClient()['meizitu']
        self.dbCollection = self.database['pics']
        self.dbIP = self.database['ips']
        self.proxy = ProxyIp.ProxyIP()
        self.currentIP = self.proxy.getIPs()

    def makeAlbumDir(self, title):
        path = os.path.join(self.rootDir, str(title).replace('?', '_'))
        self.makeDir(path)
        return path


    def makeAlbum(self, href, title,path):
        albumHtml = self.makeRequest(href)
        baseUrl = href
        albumSoup = BeautifulSoup(albumHtml.text, 'lxml')
        if len(albumSoup.select('.pagenavi span')) == 1:
            lastNumber = int(albumSoup.select('.pagenavi span')[0].string)
        else:
            lastNumber = int(albumSoup.select('.pagenavi span')[-2].string)
        imgSrces = []
        for page in range(1, lastNumber):
            imgSrc =  self.enterImageLink(baseUrl+'/'+ str(page))
            imgSrces.append(imgSrc)

        page = {
            "主题": title,
            "主题地址": baseUrl,
            "本地路径": path,
            "图片地址": imgSrces,
            "创建时间": datetime.datetime.now()
        }

        self.dbCollection.save(page)

    def randomAgent(self):
        return {'User-Agent': random.choice(self.agents)}

    def makeDir(self, path):
        if not os.path.exists(path):
            print("创建路径:" + path)
            os.mkdir(path)
        else:
            print(path + "已存在")
        print('进入' + path)
        os.chdir(path)

    def enterImageLink(self, href):
        imageHtml = self.makeRequest(href)
        imageSoup = BeautifulSoup(imageHtml.text,'lxml')
        imgSc = imageSoup.find(class_='main-image')
        if imgSc:
            imgSc = imgSc.find('img')['src']
            filename = href.split('/')[-2]+'_'+href.split('/')[-1]+imgSc.split('/')[-1]
            self.downloadPic(imgSc, filename)
            return imgSc
        else:
            return '获取失败'

    def downloadPic(self, src, filename):
        if os.path.isfile(filename):
            print("文件已存在")
            return
        print('创建图片:'+filename)
        img = self.makeRequest(src)
        file = open(filename, 'ab')
        file.write(img.content)
        file.close()

    def makeRequest(self, url):
        try:
            proxy = {'http': self.currentIP.strip()}
            print(proxy)
            response = requests.get(url, headers=self.randomAgent(), timeout=self.timeOut ,proxies=proxy,)
            print(response.text)
            return response
        except:
            self.currentIP = self.proxy.getIPs()
            self.dbIP.save({
                'IP': self.currentIP,
                'time': datetime.datetime.now()
            })
            self.tryTimes = 0
            return self.makeRequest(url)

def getNavPage(href):
    app = download()
    pageHtml = app.makeRequest(href)
    soup = BeautifulSoup(pageHtml.text, 3)
    subjectLinks = soup.select('.postlist li span:first-child a')
    for subjectLink in subjectLinks:
        title = subjectLink.text
        href = subjectLink['src']
        print(title, href)

def fuck(href):
    print(href)

if __name__ == "__main__":

    #app = download()
    #allHtml = app.makeRequest('http://www.mzitu.com')
    #allSoup = BeautifulSoup(allHtml.text, 'lxml')
    #lastLink = allSoup.select('.postlist a')[-2]
    p = Pool(2)
    for navLinkNumber in range(1, 3):
        print(navLinkNumber)
        navHref = "http://www.mzitu.com/page"+str(navLinkNumber)
        p.apply_async(getNavPage, args=(navHref,))
    p.close()
    p.join()

