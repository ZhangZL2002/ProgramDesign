from pymongo import MongoClient

import os
import csv
import time

import requests
from bs4 import BeautifulSoup
from threading import Thread

q = []


def producer():
    url_main = 'https://music.163.com/discover/playlist/?cat=流行&order=hot&limit=35&offset='
    headers = {
        "user-agent": "Mozilla / 5.0(Windows NT 10.0;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 75.0.3770.100Safari / 537.36"
    }
    for i in range(0, 1295, 35):
        url = url_main + str(i)
        response = requests.get(url=url, headers=headers)  # , headers=headers)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        # 获取包含歌单详情页网址的标签
        ids = soup.select('.dec a')
        # 获取id
        for j in range(len(ids)):
            id = ids[j]['href']
            q.append(id[13:])


def consumer():
    print('consumer thread start...')
    # 封面图片、歌单标题、创建者id、创建者昵称、介绍、歌曲数量、播放量、添加到播放列表次数、分享次数、评论数
    while len(q) == 0:
        time.sleep(0.5)

    id = q.pop()
    url = 'https://music.163.com/playlist?id=' + id
    print(url)
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    # 歌单页面
    playlist = soup.select('#m-playlist')[0]
    # 封面图片、歌单标题、创建者id、创建者昵称、介绍、歌曲数量、播放量、添加到播放列表次数、分享次数、评论数
    img_url = playlist.select('.j-img')[0]['data-src']
    title = playlist.h2.text
    user_id = playlist.select('.name a')[0]['href'][11:]
    user_name = playlist.select('.name a')[0].text
    intro = playlist.select('#album-desc-more')[0].text
    number = playlist.select('#playlist-track-count')[0].text
    play_count = playlist.select('#play-count')[0].text
    collect = playlist.select('.u-btni.u-btni-fav')[0].text
    share = playlist.select('.u-btni.u-btni-share')[0].text
    comment = playlist.select('.u-btni.u-btni-cmmt')[0].text
    img = requests.get(url=img_url)
    # 存储歌单封面图片
    if os.path.exists('images') == False:
        os.mkdir('images')
    f = open('images/playlist_' + id + ".jpg", "wb")
    f.write(img.content)
    f.close()
    # 存储歌单信息
    row = [title, user_id, user_name, intro, number, play_count[1:-1], collect[1:-1], share[1:-1], comment[1:-1]]
    if os.path.exists('song_info.csv') == False:
        with open('song_info.csv', 'w', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(
                ['歌单标题', '创建者id', '创建者昵称', '介绍', '歌曲数量', '播放量', '添加到播放列表次数',
                    '分享次数', '评论数'])
    with open('song_info.csv', 'a', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(row)


if __name__ == '__main__':
    c_list = []
    p = Thread(target=producer)
    for i in range(37):
        c = Thread(target=consumer)
        c_list.append(c)
    p.start()
    for c in c_list:
        c.start()
    for c in c_list:
        c.join()

    print('main end')
