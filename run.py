#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
import time 
import progressbar

from jinja2 import FileSystemLoader,Environment
env = Environment(loader=FileSystemLoader('templates'))



def cprint(str,debug=False):
    if(debug):
        print(str);
    pass

"""
    Config 
"""
wishOwner = "claud.xiao"
#wishOwner = "156943655" 
searchHeader = "http://my1.hzlib.net/opac/search?&q="
searchRail = "&searchWay=isbn&sortWay=score&sortOrder=desc&scWay=dim&searchSource=reader"
validSites=['文献借阅中心']
#validSites=['网易蜗牛读书馆','文献借阅中心','浣纱馆外借','西湖图书馆']
#validSites=['西湖图书馆']
printoutcnt = False



gurl = 'http://book.douban.com/people/'+wishOwner+'/wish'

user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0"
html = requests.get(url=gurl,headers={'User-Agent': user_agent}).content
soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
#cprint(soup.prettify())

# Book Page List
plist = []
for pg in soup.select('.paginator a'):
    plist.append(pg.attrs['href'])
if  len(plist)>0:
    plist.pop()


# Get the full book list
# Current page as home
blist =[]
for bk in soup.select('.subject-item .info h2 a'):
    blist.append({'title':bk.get('title'),'url':bk.get('href')})


cprint("=======================")
cprint(" Fetching Pages ")
cprint("=======================")

with progressbar.ProgressBar(max_value=len(plist)) as bar:
    i = 0
    for pg in plist:
        i = i + 1
        gurl = 'http://book.douban.com/'+pg
        time.sleep(2)
        html = requests.get(url=gurl,headers={'User-Agent': user_agent}).content
        soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
        for bk in soup.select('.subject-item .info h2  a'):
            blist.append({'title':bk.get('title'),'url':bk.get('href')})
        bar.update(i)


cprint("=======================")
cprint(" Fetching Book Details")
cprint("=======================")


bkdetails = []
# To Fetch details
with progressbar.ProgressBar(max_value=len(blist)) as bar:
    i = 0
    for bks in blist:
        i=i+1
        gurl = bks['url']
        time.sleep(2)
        html = requests.get(url=gurl,headers={'User-Agent': user_agent}).content
        soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
        infos = soup.find(id='info')
        #cprint(dir(infos.text))
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
        bks['isbn']=isbn
        bks['price']=price
        bks['dblink']=gurl
        bkdetails.append(bks)
        bar.update(i)

cprint("=======================")
cprint(" Checking Libary in: ")
cprint(validSites)
cprint("=======================")

#http://my1.hzlib.net/opac/search;jsessionid=52BF0FA6791BFB1B1BEE7D49341B5086?&q=9787540493363&searchWay=isbn&sortWay=score&sortOrder=desc&scWay=dim&searchSource=reader

def fetchBook(addr):
    time.sleep(2)
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
                time.sleep(2)
                html = requests.get(url=preaddr,headers={'User-Agent': user_agent}).content
                import json
                rec=json.loads(html)['previews'][j]
                onelocinfo=[]
                for i in rec:
                    if i['curlocalName'] in validSites:
                        onelocinfo.append({'callno':i['callno'],'curlibName':i['curlibName'],'curlocalName':i['curlocalName'],'loanableCount':i['loanableCount']})
                    else:
                        pass
                if(len(onelocinfo)>0):
                    locinfo.append(onelocinfo)
            except:
                pass
    return locinfo


bkinfos = []    

with progressbar.ProgressBar(max_value=len(bkdetails)) as bar:
    i=0
    for bk in bkdetails:
        i = i + 1
        bookname = bk['title']
        bookloc  = []
    
        ISBN=bk['isbn']
        # ISBN
        if(ISBN!="N/A"):
            pageaddr = searchHeader+ISBN+searchRail
            bookloc = fetchBook(pageaddr)
        # Book Title
        else:
            bookloc = []
        bkinfos.append({'title':bookname,'dblink':bk['dblink'], 'loc':bookloc})
        bar.update(i)

# Show Book Rec and Lib Info
# Construct json
cprint("")
cprint("")
nobook = []
outcnt = 0

libinfo  = {}
booklist = []

for bk in bkinfos:
    curbk = {}
    curbk['name'] = bk['title']
    curbk['dblink'] = bk['dblink']
    curbk['bookinfo'] = {}

    if(len(bk['loc'])==0):
        #cprint("无在馆信息")    
        nobook.append(bk['title'])
        continue
    else:
        cprint("|> 书名:《"+ bk['title'] +"》")    
        cprint("   在馆信息:")    
        for libs in bk['loc']:
            for lib in libs:
                curbk['bookinfo'] ={
                        'ID':lib['callno'],
                        'loc':lib['curlocalName'],
                        'num':lib['loanableCount']
                        }
                if(lib['loanableCount']>0):
                    cprint("")
                    cprint("#  借书号:  "+ lib['callno'])    
                    cprint("#  所在地:  "+ lib['curlocalName'])    
                    cprint("#  可出借数量:  %d"%(lib['loanableCount']))
                else:
                    if(printoutcnt):
                        cprint("")
                        cprint("#  借书号:  "+ lib['callno'])    
                        cprint("#  所在地:  "+ lib['curlocalName'])    
                        cprint("#  可出借数量:  %d"%(lib['loanableCount']))
                    outcnt=outcnt+1
            cprint("")
        booklist.append(curbk)

booklist = sorted(booklist, key=lambda x: x['bookinfo']['num'],reverse=True)

libinfo['booklist'] = booklist
libinfo['nobooklist'] = nobook

cprint(libinfo)


# Output render html
template = env.get_template('template.html')
rendered_html = template.render(bklist=libinfo)

with open('bookList.html', 'w') as output_file:
    output_file.write(rendered_html)


cprint("=========================================")
cprint("")
cprint("一共有%d本书没有图书馆记录"%(len(nobook)))
cprint("有%d本书有记录但是被借光了"%(outcnt))
cprint("")
cprint("=========================================")

bstr=""
for b in nobook:
    bstr=bstr+"|"+b
cprint(bstr)

