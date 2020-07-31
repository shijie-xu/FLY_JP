# -*- coding:utf-8 -*-

import tkinter
import re
import urllib
import urllib.request
import requests
import os


def get_homepage(url):
    req = requests.get(url)
    html = req.text
    # print(req.encoding)
    # really superised on the encoding!
    return html


def get_items(html):
    pattern = re.compile(
        r'<a href="(http://.+?)" title=".+?" target="_blank">.+?</a>')
    return re.findall(pattern, html)


if __name__ == '__main__':
    homepage_url = r'http://www.kekenet.com/broadcast/Normal/'
    html = get_homepage(homepage_url)
    items = get_items(html)
    for url in items:
        # get news homepage
        content = get_homepage(url)
        # get title
        pattern_title = re.compile(
            r'<h1 id="nrtitle">(.+?)</h1>')
        title = pattern_title.findall(content)[0].encode(
            'ISO-8859-1').decode('utf-8')
        # print(title)
        # get mp3
        pattern_mp3_page = re.compile(
            r'<a target="_blank" href="(/mp3/.+?)">'
        )
        mp3_page = r'http://www.kekenet.com' + \
            pattern_mp3_page.findall(content)[0]

        mp3_content = get_homepage(mp3_page)
        pattern_downlink = re.compile(
            r'<a target="_blank" href="(http://.+?mp3)"')
        downlink = pattern_downlink.findall(mp3_content)
        # try to retrieve mp3
        for link in downlink:
            try:
                down_name = title.replace(':', ' ')+".mp3"
                if (os.path.exists(down_name)):
                    break
                urllib.request.urlretrieve(
                    link, down_name)
                print('downloading '+title+' ...')
                break
            except:
                continue
