import pymongo
import requests
import time
from bs4 import BeautifulSoup
import os
import threading
import gevent

song_id = []
song_information = []

headers = {
    'Referer': 'http://music.163.com/',
    'Host': 'music.163.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}


def productor():
    print("productor starts")
    global song_id
    for i in range(0, 35, 35):
        url = 'https://music.163.com/discover/playlist/?order=hot&cat=流行&limit=35&offset=' + str(i)
        response = requests.get(url=url, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        # 获取包含歌单详情页网址的标签
        ids = soup.select('.dec a')
        # 获取包含歌单索引页信息的标签
        lis = soup.select('#m-pl-container li')
        for j in range(len(lis)):
            song_id.append(ids[j]['href'][13:])
    time.sleep(0.1)
    print(len(song_id))
    print("productor ends")


def consumer(Number):
    print("consumer {} starts".format(Number))
    global song_id, song_information
    id = song_id.pop()
    url = 'https://music.163.com//playlist?id=' + id
    response = requests.get(url=url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.select('#m-playlist')
    # 获取封面图片并保存在相应文件夹
    img_url = lis[0].select('.j-img')[0]['data-src']
    title = lis[0].select('.tit')[0].text
    # 获取创建者id、昵称
    creator_id = lis[0].select('.name a')[0]['href'][11:]
    creator_name = lis[0].select('.name')[0].text
    # 获取歌曲介绍
    introduction = lis[0].select('#album-desc-more')[0].text
    # 获取歌单日期
    date = lis[0].select('.time.s-fc4')[0].text
    # 获取歌曲数量
    number = lis[0].select('#playlist-track-count')[0].text
    # 获取歌曲播放量
    play = lis[0].select('#play-count')[0].text
    # 获取添加到播放列表次数
    add = lis[0].select('.u-btni.u-btni-fav')[0].text
    # 获取分享次数
    share = lis[0].select('.u-btni.u-btni-share')[0].text
    # 获取评论数
    comment = lis[0].select('.u-btni.u-btni-cmmt')[0].text
    song_information.append({"ID": id, "title": title, "author": creator_name, "date": date, "image_path": img_url})


def insert(text):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["database_zzl"]  # 创建数据库
    mycol = mydb["WangYi_info"]  # 创建集合
    mycol.insert_many(text)


if __name__ == '__main__':
    tasks = []
    for i in range(35):
        tasks.append(gevent.spawn(consumer, i))
    productor()
    gevent.joinall(tasks)
    insert(song_information)
