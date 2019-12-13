#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
import time 
import progressbar

"""
    Config 
"""
wishOwner = "claud.xiao"
#wishOwner = "156943655"
searchHeader = "http://my1.hzlib.net/opac/search?&q="
searchRail = "&searchWay=isbn&sortWay=score&sortOrder=desc&scWay=dim&searchSource=reader"
validSites=['网易蜗牛读书馆','文献借阅中心','浣纱馆外借']


gurl = 'http://book.douban.com/people/'+wishOwner+'/wish'

user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0"
html = requests.get(url=gurl,headers={'User-Agent': user_agent}).content
soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
#print(soup.prettify())

# Book Page List
plist = []
for pg in soup.select('.paginator a'):
    plist.append(pg.attrs['href'])
if  len(plist)>0:
    plist.pop()
print(plist)


# Get the full book list
# Current page as home
blist =[]
for bk in soup.select('.subject-item .info h2 a'):
    blist.append([bk.get('title'),bk.get('href')])


print("=======================")
print(" Fetching Pages ")
print("=======================")

with progressbar.ProgressBar(max_value=len(plist)) as bar:
    i = 0
    for pg in plist:
        i = i + 1
        gurl = 'http://book.douban.com/'+pg
        html = requests.get(url=gurl,headers={'User-Agent': user_agent}).content
        soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
        for bk in soup.select('.subject-item .info h2  a'):
            blist.append([bk.get('title'),bk.get('href')])
        bar.update(i)


print("=======================")
print(" Fetching Book Details")
print("=======================")


bkdetails = []
# To Fetch details
with progressbar.ProgressBar(max_value=len(blist)) as bar:
    i = 0
    for bks in blist:
        i=i+1
        gurl = bks[1]
        html = requests.get(url=gurl,headers={'User-Agent': user_agent}).content
        soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
        infos = soup.find(id='info')
        #print(dir(infos.text))
        rawt = infos.text
        rPlacer= re.compile(r".*(ISBN)[^\d]*(\d+).*", re.M)
        isbn = rPlacer.search(rawt)
        if isbn:
            isbn = isbn.group(2)
        else:
            isbn = "N/A"
        rPlacer= re.compile(r".*(定价)[^\d]*(\d+).*", re.M)
        price = rPlacer.search(rawt)
        if price:
            price = price.group(2)
        else:
            price = "N/A"
        bks = bks + [isbn, price]
        bkdetails.append(bks)
        bar.update(i)

print("=======================")
print(" Checking Libary ")
print("=======================")

#http://my1.hzlib.net/opac/search;jsessionid=52BF0FA6791BFB1B1BEE7D49341B5086?&q=9787540493363&searchWay=isbn&sortWay=score&sortOrder=desc&scWay=dim&searchSource=reader

def fetchBook(addr):
    html = requests.get(url=addr,headers={'User-Agent': user_agent}).content
    soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
    #import pdb
    #pdb.set_trace()
    infos = soup.select('.bookmetaTitle a')
    locinfo = []
    if(len(infos)==0):
        return []
    else:
        bid = []
        for i in infos:
            bid.append(i.attrs['id'].replace('title_',''))

        for j in bid:
            try:
                preaddr = "http://my1.hzlib.net/opac/book/holdingPreviews?bookrecnos="+j+"&curLibcodes=&return_fmt=json"
                html = requests.get(url=preaddr,headers={'User-Agent': user_agent}).content
                import json
                rec=json.loads(html)['previews'][j]
                onelocinfo=[]
                for i in rec:
                    if i['curlocalName'] in validSites:
                        onelocinfo.append([i['callno'],i['curlibName'],i['curlocalName'],i['loanableCount']])
                    else:
                        pass
                if(len(onelocinfo)>0):
                    locinfo.append(onelocinfo)
            except:
                pass
    return locinfo
bkinfos = []    
for bk in bkdetails:
    bookname = bk[0]
    bookloc  = []

    ISBN=bk[2]
    # ISBN
    if(ISBN!="N/A"):
        pageaddr = searchHeader+ISBN+searchRail
        bookloc = fetchBook(pageaddr)
    # Book Title
    else:
        bookloc = []
    bkinfos.append([bookname, bookloc])

# Show Book Rec and Lib Info
print("书籍借阅信息")
for bk in bkinfos:
    print("")
    print(">    书名:《"+ bk[0] +"》")    
    if(len(bk[1])==0):
        print("无在馆信息")    
    else:
        print("在馆信息:")    
    for libs in bk[1]:
        for lib in libs:
            print("    #  借书号:  "+ lib[0])    
            print("    #  所在地:  "+ lib[2])    
            print("    #  可出借数量:  %d"%(lib[3]))
        print("")
