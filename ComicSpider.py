from config import *
import requests
import re
from bs4 import BeautifulSoup
import os
import time
import sys
def mkd(ml):
    if os.path.exists(ml) == False:
        try:
            os.mkdir(ml)
        except:
            print("文件夹创建失败,重新创建")
            os.mkdir(ml)
    else:
        print("该文件夹已存在,跳过")
def get_manhua_list(url):
    try:
        req1 = requests.get(url, headers=HEADERS)
        manhua_html = req1.text
        soup = BeautifulSoup(manhua_html, 'lxml')
        ml = soup.select('#Head1 title')
        ml = ml[0].get_text()
        ml = ml.replace(" ", "")
        ml = ml.replace("\n", "")
        ml = ml.replace("\r", "")
        ml = ml.lstrip()
        ml = os.getcwd() + "/" + ml
        print("创建文件夹:", ml)
        mkd(ml)
        print("文件夹创建成功")
        os.chdir(ml)
        print("进入文件夹:", ml)
        manhua_list_url = soup.select('.l_s')
        return manhua_list_url
    except:
        print('失败:重新获取漫画目录请求链接')
        get_manhua_list(url)
def get_list_url(manhua_list_url):
    try:
        for i in reversed(manhua_list_url):
            list_url_title = i['title']
            list_url_href = i['href']
            list_url_href = 'http://www.hhimm.com' + list_url_href

            yield  {
                'list_url_title' : list_url_title,
                'list_url_href' : list_url_href
            }
    except:
        print('失败:重新获取完整的目录链接')
        get_list_url(manhua_list_url)
def manhua_get_page(list_url_href):
    try:
        req2 = requests.get(list_url_href, headers=HEADERS)
        manhua_image_html = req2.text
        soup = BeautifulSoup(manhua_image_html, 'lxml')
        for i in soup.select('.cH1 b'):
            manhua_total_page = (i.get_text())[-2:]
            return manhua_total_page
    except:
        print('失败:重新获取漫画章节的图片数量')
        manhua_get_page(list_url_href)
def get_image_url(list_url_href_page):
    try:
        req3 = requests.get(list_url_href_page, headers=HEADERS)
        get_image_html = req3.text
        soup = BeautifulSoup(get_image_html, 'lxml')
        image_source = soup.select('#hdDomain')
        source = img_url_analysis(image_source)
        res = re.compile(r'<img id=".*" name="(\w*)".*value="\w*"')
        ff = re.findall(res,get_image_html)
        s = img_url_analysis2(ff)
        img_url = source+s

        return img_url
    except:
        print('失败:重新获取漫画图片的链接')
        get_image_url(list_url_href_page)

def img_url_analysis(image_source):
    try:
        for i in image_source:
            source = i['value']
            arrDS = source.split('|')
            return arrDS[0]
    except:
        img_url_analysis(image_source)
def img_url_analysis2(sss):
    try:
        s = sss[0]
        x = s[(len(s) - 1):]
        w = "abcdefghijklmnopqrstuvwxyz"
        xi = w.index(x) + 1
        sk = s[len(s) - xi - 12 : len(s) - xi - 1]
        s = s[0 : len(s) - xi - 12]
        k = sk[0 : len(sk) - 1]
        f = sk[(len(sk) - 1):]
        for i in range(len(k)):
            s = s.replace(k[i: i + 1], str(i))
        ss = s.split(f)
        s = ""
        for i in range(len(ss)):
            iii = int (ss[i])
            s = s + chr(iii)
        return s
    except:
        img_url_analysis2(sss)
def down(img_url, zz):
    try:
#        proxies = 'http://' + get_proxy()
#        proxy = {'http': proxies}
#        print("使用代理ip:", proxy)
        print("发送图片下载请求")
        req4 = requests.get(img_url, headers=HEADERS , timeout=10)
        print("图片开始下载")
        if not os.path.exists(zz):
            with open(zz, 'wb') as f:
                print('下载图片',zz)
                f.write(req4.content)
        print("图片下载成功")
    except:
        print('下载超时:重新下载图片文件')
        down(img_url, zz)
def main():
    rrr = sys.argv[1]
    manhua_list_url = get_manhua_list(rrr)
    cc = get_list_url(manhua_list_url)
    for i in cc:
        list_url_href = i['list_url_href']
        list_url_title = i['list_url_title']
        total_page = manhua_get_page(list_url_href)
        print("总共:", total_page, "页")
        list_url_href = re.sub(r'/\d+.html', '/PAGE.html', list_url_href)
        print('获取的章节链接为:', list_url_href)
        if os.path.exists(list_url_title) == False:
            os.mkdir(list_url_title)
        print("创建漫画文件夹", list_url_title)
        for i in range(1,int(total_page)+1):
            dd = '/'+str(i)+'.html'
            print('第', i ,"页")
            list_url_href_page = re.sub(r'/PAGE.html', dd, list_url_href) + '&d=0'
#            print(list_url_href_page)
            img_url = get_image_url(list_url_href_page)
            print('图片链接为:', img_url)
            zz = list_url_title + '/' + str(i) + '.jpg'
            time.sleep(2.7)
            down(img_url, zz)
if __name__ == '__main__':
    main()
    print("此漫画全部下载完成!!!!")