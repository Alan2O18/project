import requests
from bs4 import BeautifulSoup
import datetime
import re
from threading import Timer
import time
import threading
# import sys

# sys.stdout = open("log.txt","w",encoding="UTF-8")

headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
         'Referer': 'https://www.ptt.cc/'}

url = ""
urlChange = False

nextTimeTemple = [" 08:30:00"," 14:00:00"]

def getUrl():
    print("start get url...")
    global url
    global urlChange
    resp = requests.get('https://www.ptt.cc/bbs/Stock/index.html',headers=headers)
    if resp.status_code == requests.codes.ok:
        print("HTTPS respond OK")
        soup = BeautifulSoup(resp.text, 'html.parser')
        stories = soup.find_all('div', class_='r-ent')
        for s in stories:
            s = str(s)
            tmp = BeautifulSoup(s, 'html.parser')
            tnp = tmp.find_all("a",href = True)
            for i in tnp:
                if re.match(r"\[閒聊\] .......... 盤後閒聊",i.text) or  re.match(r"\[閒聊\] .......... 盤中閒聊",i.text):
                    urlTmp = "https://www.ptt.cc" + i.get('href')
                    print("find text = " + i.text)
                    print("find url = " + urlTmp)
                    if urlTmp != url:
                        url = urlTmp
                        urlChange = True
                        print("url change")
                        break
        print("done")
    else:
        print("HTTPS respond error" + str(resp.status_code))

def getData():
    print("get data...")
    print("url = " + url)
    resp = requests.get(url, headers=headers)
    if resp.status_code == requests.codes.ok:
        print("HTTPS respond OK")
        soup = BeautifulSoup(resp.text, 'html.parser')
        stories = soup.find_all('div', class_='push')
        lastTime = ""
        with open("lastTime.txt","r",encoding="UTF-8") as ft:
            lastTime = ft.readline()
            lastTime = datetime.datetime.strptime(lastTime,"%Y-%m-%d %H:%M:%S")
        for s in stories:
            s = str(s)
            tmp = BeautifulSoup(s, 'html.parser')
            tnp = tmp.find("span",class_="f3 hl push-userid")
    
            if tnp == None:
                print("not find span maybe normal")
            elif tnp.text == "f204137     " or tnp.text == "guilty13    " or tnp.text == "a0808996    ":
                result = tmp.find("span",class_="f3 push-content")
                time = tmp.find("span",class_="push-ipdatetime")
                time = datetime.datetime.strptime(time.text," %m/%d %H:%M\n")
                if(time >= lastTime):
                    lastTime = time
                    with open("data2.txt",'a',encoding="UTF-8") as fs:
                        fs.write("id= " + tnp.text + " text= " + result.text + "\n")
        with open("lastTime.txt","w",encoding="UTF-8") as ft:
            ft.write(str(lastTime))
        print("done")
    else:
        print("HTTPS respond error" + str(resp.status_code))

class RepeatingTimer(Timer): 
    def run(self):
        self.finished.wait(self.interval)
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)

t = RepeatingTimer(600,getData)

while True:
    nextTimeGetUrl = ""
    now = datetime.datetime.now()
    with open("nextTimeGetUrl.txt","r",encoding="UTF-8") as ft:
            nextTimeGetUrl = ft.readline()
            nextTimeGetUrl = datetime.datetime.strptime(nextTimeGetUrl,"%Y-%m-%d %H:%M:%S")

    if now >= nextTimeGetUrl:
        getUrl()
        Todaylast = str(datetime.date.today()) + nextTimeTemple[1]
        if now > datetime.datetime.strptime(Todaylast,"%Y-%m-%d %H:%M:%S"):
            nextday = str(datetime.date.today() + datetime.timedelta(days=1))
            nextTimeGetUrl = datetime.datetime.strptime(nextday + nextTimeTemple[0],"%Y-%m-%d %H:%M:%S")
        else:
            nextday = str(datetime.date.today())
            nextTimeGetUrl = datetime.datetime.strptime(nextday + nextTimeTemple[1],"%Y-%m-%d %H:%M:%S")

        print("Next time get url = " + str(nextTimeGetUrl))
        with open("nextTimeGetUrl.txt","w",encoding="UTF-8") as ft:
            ft.write(str(nextTimeGetUrl))
        if urlChange:
            urlChange = False
            t.start()
            print("getData start")
        else:
            print("getData cancel reason = no new url")
            t.cancel()
            time.sleep(1800)
    else:
        time.sleep(3600)