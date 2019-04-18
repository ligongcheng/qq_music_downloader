#!usr/bin/env python
# -*- coding: UTF-8 -*-
import traceback

import requests, re, os, time
import sys

api_url = 'https://api.bzqll.com/music/tencent/songList?key=579621905&id='
m_id = '6940396907'  # 歌单的id
path = os.getcwd() + '\\music\\' + m_id + '\\'  # 保存的路径


# 保存歌曲
def save_song(url, singer, name, lrc):
    global path
    if not os.path.exists(path):
        os.makedirs(path)
    mp3_path = path + name + '-' + singer + ".mp3"
    flac_path = path + name + '-' + singer + ".flac"
    if os.path.exists(mp3_path):
        if os.path.getsize(mp3_path) > 0:
            print('exist skip  ' + name + '-' + singer)
            return
    if os.path.exists(flac_path):
        if os.path.getsize(flac_path) > 0:
            print('exist skip  ' + name + '-' + singer)
            return
    resource = get_page(url + '&br=flac', True)
    if resource.status_code != 200:
        r = get_page(url + '&br=320', True)
        if r.status_code == 200:
            with open(mp3_path, mode="wb") as fh:
                print('dl ' + mp3_path)
                dl_lrc(singer, name, lrc)
                fh.write(r.content)
        return
    # 下载歌曲并保存
    with open(flac_path, mode="wb") as fh:
        fh.write(resource.content)
        dl_lrc(singer, name, lrc)
        print('dl ' + flac_path)


def dl_lrc(singer, name, lrc):
    global path
    lrc_path = path + name + '-' + singer + ".lrc"
    resource = get_page(lrc, False)
    with open(lrc_path, mode="w", encoding='utf-8') as fh:
        fh.write(resource.text)


def get_page(url, stream):
    su = False
    num = 5
    r = None
    while not su and num > 0:
        try:
            r = requests.get(url, stream=stream, timeout=3)
            su = True
        except:
            print('timeout retry')
            num = num - 1
    return r


def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "", title)  #
    return new_title.strip()


if __name__ == '__main__':
    s = input("输入qq音乐歌单id例如 6940396907 :")
    if len(str(s).strip()) != 10:
        print('请输入正确的10位id号')
        time.sleep(1)
        sys.exit()
    m_id = str(s).strip()
    r = requests.get(api_url + m_id)
    response_dict = r.json()
    res = response_dict['data']['songs']
    lenght = response_dict['data']['songnum']
    print('total ' + str(lenght))
    for i in range(int(lenght)):
        mode = 1
        name = res[i]['name']
        name = validateTitle(name)
        url = res[i]['url']
        lrc = res[i]['lrc']
        singer = res[i]['singer'].replace('/', '&')
        try:
            save_song(url, singer, name, lrc)
        except Exception as e:
            print('error ' + name)
            traceback.print_exc()
