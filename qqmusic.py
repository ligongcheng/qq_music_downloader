#!usr/bin/env python
# -*- coding: UTF-8 -*-

'''

链接内容(QQ音乐支持)：
    歌曲链接 如 https://y.qq.com/n/yqq/song/003Afb7F2LwcmR.html
    歌单链接 如 https://y.qq.com/n/yqq/playlist/863753969.html 或 https://y.qq.com/n/yqq/playsquare/4160828085.html#stat=y_new.playlist.dissname
    专辑链接 如 https://y.qq.com/n/yqq/album/004QbYQU4CB1Zi.html 开发中
    歌曲搜索 开发中 半成品
'''

import json
import os
import re
import time

import requests

headers = {'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 5.1.1; vivo x5s l Build/LMY48Z)',
           'Referer': 'https://y.qq.com/portal/profile.html'}

qq_re = re.compile(r'(\w+)\.html')

size_list = ['size_128mp3', 'size_320mp3', 'size_ape', 'size_flac']

dl = True

down_type = 'size_flac'


def get_key():
    uin = '1008611'
    guid = '1234567890'
    getVkeyUrl = 'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?g_tk=0&loginUin={uin}&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&cid=205361747&uin={uin}&songmid=003a1tne1nSz1Y&filename=C400003a1tne1nSz1Y.m4a&guid={guid}'
    url = getVkeyUrl.format(uin=uin, guid=guid)
    try:
        r = requests.get(url, headers=headers)
        json = r.json()
        vkey = json['data']['items'][0]['vkey']
        if len(vkey) == 112:
            return vkey
    except:
        pass
    return None


def format(size):
    return '{0:.1f}'.format(size)


def download(single_info, down_path):
    if not dl:
        return
    if not os.path.exists(down_path):
        os.makedirs(down_path)

    if down_type not in size_list:
        print('输入格式错误')
    length = len(single_info['link_info'])
    try:
        url = single_info['link_info'][down_type]['link']
    except:
        url = single_info['link_info'][size_list[length - 1]]['link']
    type = re.search(r'(mp3|ape|flac)', url).group(0)
    song_name = single_info['song_name'] + '-' + single_info['singer_name'] + '.' + type
    song_path = down_path + '/' + song_name
    if os.path.exists(song_path):
        getsize = os.path.getsize(song_path)
        if getsize == 0:
            os.remove(song_path)
        else:
            print('already exist:{0} skip'.format(song_name))
            return

    print('start download:', song_name)
    with requests.get(url, headers=headers, stream=True) as r:
        with open(song_path, mode='wb') as f:
            f.write(r.content)
    print('download success')


def get_single_info(songmid, vkey, do=True):
    info_url = 'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid={songmid}&tpl=yqq_song_detail&format=json&callback=getOneSongInfoCallback&g_tk=5381&jsonCallback=getOneSongInfoCallback&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'
    url = info_url.format(songmid=songmid)
    try:
        r = requests.get(url=url, headers=headers)
        json = r.json()
        music_info = json['data'][0]['file']
        media_mid = json['data'][0]['file']['media_mid']
        song_name = json['data'][0]['name']
        singer_name = json['data'][0]['singer'][0]['name']
        album_name = json['data'][0]['album']['name']
        single_info = {'singer_name': singer_name, 'song_name': song_name, 'album_name': album_name,
                       'media_mid': media_mid}
        song_link = get_link(media_mid, vkey)
        link_info = {}
        for i in range(0, 4):
            s = format(music_info[size_list[i]] / 1024 / 1024)
            if s == '0.0':
                continue
            link_info[size_list[i]] = {'size': s, 'link': song_link[i]}
        single_info['link_info'] = link_info
        down_path = os.getcwd() + '/song'
        try:
            if do:
                download(single_info, down_path)
        except:
            print('download fail')
        return single_info
    except:
        pass
    return None


def get_playlist_info(playlist_id, vkey):
    list_url = 'https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?type=1&json=1&utf8=1&onlysong=0&disstid={playlist_id}&format=jsonp&g_tk=5381&jsonpCallback=playlistinfoCallback&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'
    url_format = list_url.format(playlist_id=playlist_id)
    r = requests.get(url_format, headers=headers)
    text = r.text
    s = text.lstrip('playlistinfoCallback(').rstrip(')')
    json_loads = json.loads(s)
    cdlist_info = json_loads['cdlist'][0]
    playlist_name = cdlist_info['dissname']
    playlist_desc = cdlist_info['desc']
    playlist_logo = cdlist_info['logo']
    info_songlist = cdlist_info['songlist']
    playlist_info = {'name': playlist_name, 'desc': playlist_desc, 'logo': playlist_logo}
    songlist = []
    down_path = os.getcwd() + '/playlist/' + playlist_name
    for item in info_songlist:
        songmid = item['songmid']
        info = get_single_info(songmid, vkey, do=False)
        download(info, down_path)
        songlist.append(info)
    playlist_info['songlist'] = songlist
    return playlist_info


def get_link(media_mid, vkey):
    type_info = [['M500', 'mp3'], ['M800', 'mp3'], ["A000", 'ape'], ['F000', 'flac']]
    dl_url = 'http://streamoc.music.tc.qq.com/{prefix}{media_mid}.{type}?vkey={vkey}&guid=1234567890&uin=1008611&fromtag=8'
    dl = []
    for item in type_info:
        s_url = dl_url.format(prefix=item[0], media_mid=media_mid, type=item[1], vkey=vkey)
        dl.append(s_url)
    return dl


def search(page_num, page_size, song_name):
    search_url = 'http://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&new_json=1&remoteplace=txt.yqq.center&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p={page_num}&n={page_size}&w={song_name}&jsonpCallback=searchCallbacksong2020&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'.format(
        page_num=page_num, page_size=page_size, song_name=song_name)
    r = requests.get(search_url, headers=headers)
    json = r.json()
    return json


def parse_song(link):
    songmid = qq_re.search(link)[1]
    return songmid


def parse_playlist(link):
    playlist_id = qq_re.search(link)[1]
    return playlist_id


if __name__ == '__main__':
    vkey = get_key()

    if vkey == None:
        print('获取key失败，正在退出。。。')
        time.sleep(2)
        os._exit(1)

    print('''
    欢迎使用qq音乐下载工具
    支持地址如下：
    歌曲链接 如 https://y.qq.com/n/yqq/song/003Afb7F2LwcmR.html
    歌单链接 如 https://y.qq.com/n/yqq/playlist/863753969.html 或 https://y.qq.com/n/yqq/playsquare/4160828085.html#stat=y_new.playlist.dissname
    专辑链接 如 https://y.qq.com/n/yqq/album/004QbYQU4CB1Zi.html 开发中...
    歌曲搜索 开发中 半成品...
    下载歌曲格式 128mp3 , 320mp3 , ape , flac  若无选择的音质则默认下载音质最好的
    输入链接时输入 q 退出本工具
    
    输入序号(0,1,2,3)
    
    0. 代表128kmp3 
    1. 代表320kmp3
    2. 代表ape
    3. 代表flac 
    
    ''')

    in_down_type = input("输入序号,按回车默认flac:")
    if in_down_type is "" or int(in_down_type) not in range(0, 4):
        print('格式:flac')
    else:
        down_type = size_list[int(in_down_type)]
        print('格式:', down_type)

    while True:
        link = str(input('请输入链接:'))
        if link == 'q' or 'qq.com' not in link:
            print('正在退出。。。')
            os._exit(1)
        if 'song' in link:
            print('该链接为qq歌曲链接，正在解析。。。')
            song = parse_song(link)
            info = get_single_info(song, vkey)
            # print(info)
        elif 'playlist' in link or 'playsquare' in link:
            print('该链接为qq歌单链接，正在解析。。。')
            playlist_id = parse_playlist(link)
            playlist_info = get_playlist_info(playlist_id, vkey)
            # print(playlist_info)
        elif 'album' in link:
            print('该链接为qq专辑链接，正在开发中。。。')
        else:
            print('链接错误')

    # search1 = search(1, 10, '遇')
    # print(search1)
