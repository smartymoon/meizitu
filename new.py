import multiprocessing ,ProxyIp ,datetime, random, os
import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup

class App:
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
        self.proxy = ProxyIp.ProxyIP()
        self.rootDir = 'D:\mzitu'
        self.getNewIP()
        self.dbCollection = MongoClient()['meizitu']['pics']

        self.makeDir(self.rootDir)

    def makeDir(self, path):
        if not os.path.exists(path):
            print("路径不存在")
            os.mkdir(path)
        print("路径已存在")
        os.chdir(path=path)

    def getNewIP(self):
        self.currentIP = self.proxy.getIP()


    def makeRequest(self, url):
        ip = self.currentIP
        headers = {"User-Agent": random.choice(self.agents)}
        try:
            if ip == None:
                return requests.get(url, timeout=3, headers=headers)
            else:
                proxies = {'proxy': ip}
                return requests.get(url, timeout=3, headers=headers, proxies=proxies)
        except:
            self.getNewIP()
            return self.makeRequest(url)

    def dealSubject(self, title, href):
        print('start dealSubject')
        path = os.path.join(self.rootDir, str(title).replace('?', "_"))
        if self.dbCollection.find({"主题": title}).count() != 0:
            print("主题已存在")
            return
        self.makeDir(path)
        images = self.makeImages(href)
        post = {
            "主题": title,
            "imageInfo": images,
            "主题地址": path,
            "创建时间": datetime.datetime.now()
        }
        self.dbCollection.save(post)

    def makeImages(self, url):
        print("makeImages", url)
        subjectHtml = self.makeRequest(url)
        soup = BeautifulSoup(subjectHtml.text, 'lxml')
        lastImagePageNumber = int(soup.select('.pagenavi a')[-2].text)
        imageHrefs = []
        for i in range(1, lastImagePageNumber+1):
            imageHrefs.append(url + "/" + str(i))
        images = []
        for href in imageHrefs:
            images.append(self.getImage(href))
        return images


    def getImage(self, url):
        imagePage = self.makeRequest(url)
        soup = BeautifulSoup(imagePage.text, 'lxml')
        src = soup.find(class_="main-image").find('img')['src']
        filename = url.split('/')[-2]+'_'+url.split('/')[-1]+'_'+src.split('/')[-1]
        return self.saveImage(src, filename)

    def saveImage(self, src, filename):
        if os.path.isfile(filename):
            print('文件已存在')
        else:
            image = self.makeRequest(src)
            f = open(filename, 'ab')
            f.write(image.content)
            f.close()
            print("save image")
        return {"src": src, "path": os.path.abspath(filename), "name": filename}
def enterPage(link):
    app = App()
    soup = BeautifulSoup(app.makeRequest(link).text, "lxml")
    subjects_li = soup.select(".postlist li")
    subjects = []
    for li in subjects_li:
        subjects.append(li.find('span').find('a'))
    for subject in subjects:
        title = subject.text
        href = subject['href']
        app.dealSubject(title, href)

if __name__ == "__main__":
    mzitu = "http://www.mzitu.com"
    app = App()
    cpu_number = multiprocessing.cpu_count()
    homePage = app.makeRequest(mzitu)
    soup = BeautifulSoup(homePage.text, 'lxml')
    lastLink = soup.select('.postlist a')[-2]
    links = []
    for i in range(1, int(lastLink.text) + 1):
        links.append(mzitu + "/page/" + str(i))

    lock = multiprocessing.Lock()
    pool = multiprocessing.Pool(processes=cpu_number)
    for link in links:
        #enterPage(link)
        pool.apply_async(enterPage, args=(link,))
    pool.close()
    pool.join()
