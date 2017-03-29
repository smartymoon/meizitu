import random

import requests
from bs4 import BeautifulSoup
import os
class download:
    rootDir = 'D:\mzitu'
    agents  = [
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

    def getAll(self, url):
        allHtml = requests.get(url, headers=self.randomAgent())
        allSoup = BeautifulSoup(allHtml.text, 'lxml')
        allLink = allSoup.select('.archives a')
        for a in allLink:
            title = a.string
            href = a['href']
            self.makeAlbumDir(title)
            self.makeAlbum(href)

    def makeAlbumDir(self, title):
        path = os.path.join(self.rootDir, str(title).replace('?','_'))
        self.makeDir(path)


    def makeAlbum(self, href):
        albumHtml = requests.get(href, headers=self.randomAgent())
        baseUrl = href
        albumSoup = BeautifulSoup(albumHtml.text, 'lxml')
        lastNumber = int(albumSoup.select('.pagenavi span')[-2].string)
        for page in range(1, lastNumber):
            self.enterImageLink(baseUrl+'/'+ str(page))

    def randomAgent(self):
        return {'User-Agent': random.choice(self.agents)}

    def makeDir(self,path):
        if not os.path.exists(path):
            print("创建路径:" + path)
            os.mkdir(path)
        else:
            print(path + "已存在")
        print('进入' + path)
        os.chdir(path)

    def enterImageLink(self, href):
        imageHtml = requests.get(href, headers=self.randomAgent())
        imageSoup = BeautifulSoup(imageHtml.text,'lxml')
        imgSc = imageSoup.find(class_='main-image').find('img')['src']
        filename = href.split('/')[-2]+'_'+href.split('/')[-1]+imgSc.split('/')[-1]
        self.downloadPic(imgSc,filename)

    def downloadPic(self, src, filename):
        if os.path.isfile(filename):
            print("文件已存在")
            return
        print('创建图片:'+filename)
        img = requests.get(src, headers=self.randomAgent())
        file = open(filename, 'ab')
        file.write(img.content)
        file.close()

    def makeRequest(self, url):
        return requests.get(url, headers=self.randomAgent())




app =  download()
#app.getAll('http://www.mzitu.com/all')
