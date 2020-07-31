import tkinter
import tkinter.messagebox
import urllib
import urllib.request
import time
import re
import webbrowser
import os


def get_home_content(home_url):
    response = urllib.request.urlopen(home_url)
    html = response.read().decode('utf-8')
    # print(html)
    pattern = re.compile(
        r'<a href="/VOA_Special_English/([a-zA-Z/\-_0-9\.]+?)" target="_blank">([a-zA-Z()/0-9 ]+?)</a>')
    match_list = pattern.findall(html)
    # return match_list[0][1] + sub_url + match_list[0][0]
    return match_list


def get_article_content(url):
    response = urllib.request.urlopen(url)
    html = response.read().decode('utf-8')
    # fileOut = open('html.html', 'w')
    # fileOut.write(html)
    # fileOut.flush()

    pattern = re.compile(
        r'mp3:"([a-zA-Z/:\.\-_0-9]+?)"'
    )
    match_MP3 = pattern.findall(html)[0]
    pattern_text = re.compile(
        r'(\[[0-9]{2}:[0-9]{2}.[0-9]{2}\])(.+?)\n'
    )
    match_lyr = pattern_text.findall(html)

    pattern_cover = re.compile(
        r'<div class="contentImage"><img src="(.+?)"'
    )
    match_img = pattern_cover.findall(html)[0]
    return (match_MP3, match_lyr, match_img)


url = r'https://www.51voa.com/'
sub_url = url+'VOA_Special_English/'
mp3_path = ''
clip = None
articleList = []
urlList = []
progress = ''

window = tkinter.Tk()
window.geometry("600x480")
window.title("VOA News")

# add listbox
listBox = tkinter.Listbox(window, font=("Times New Roman", 12))


def showNewWindow(event):
    # ex_window = tkinter.Tk()
    # ex_window.state("zoomed")#only for windows system
    cur_idx = listBox.curselection()[0]
    title = articleList[cur_idx]
    url = urlList[cur_idx]

    ret = get_article_content(sub_url+url)
    MP3_url = ret[0]
    lyrics = ret[1]
    img = ret[2]

    fileLyr = open((title+'.lrc').replace('/', '.'), 'w')
    idx = 0
    for item in lyrics:
        if idx == 0:
            idx += 1
            continue
        fileLyr.write(item[0]+item[1])
        fileLyr.flush()
    fileLyr.close()

    mp3_path = (title+".mp3").replace('/', '.')
    #clip = mp3play.load(mp3_path)
    # clip.play()

    urllib.request.urlretrieve(MP3_url, mp3_path)

    tkinter.messagebox.askokcancel('Infomation', mp3_path+' was downloaded!')

    img_path = (title+".jpg").replace('/', '.')
    print(img)
    urllib.request.urlretrieve(img, img_path)
    # ex_window.mainloop()


content = get_home_content(url)

for item in content:
    _url = item[0]
    _title = item[1]
    articleList.append(_title)
    urlList.append(_url)
    listBox.insert(tkinter.END, _title)

listBox.pack(fill=tkinter.BOTH, expand=tkinter.YES, side=tkinter.TOP)
listBox.bind('<Double-Button-1>', showNewWindow)
label = tkinter.Label(window, textvariable=progress).pack(
    fill=tkinter.BOTH, expand=tkinter.NO, side=tkinter.BOTTOM)

window.mainloop()
