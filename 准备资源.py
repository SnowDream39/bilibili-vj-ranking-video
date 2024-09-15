import pandas as pd
import numpy as np
import json
import asyncio
from datetime import datetime, timedelta
from bilibili_api import video, Credential, HEADERS, sync
import requests
from PIL import Image
from io import BytesIO
import httpx
import yaml
import os
import shutil
import argparse


#开头常量部分

FFMPEG_PATH = "D:/Tool/ffmpeg-2024-07-07-git-0619138639-full_build/bin/ffmpeg.exe"


now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
today = now - timedelta(days=1)
full_date = today.strftime("%Y.%m.%d")
themes = {
    0: "周日主题色",
    1: "周一主题色",
    2: "周二主题色",
    3: "周三主题色",
    4: "周四主题色",
    5: "周五主题色",
    6: "周六主题色",
}
with open("截取片段.json", "r", encoding="utf-8") as file:
    clip_points = json.load(file)


async def download_url(url: str, out: str, info: str):
    # 下载函数
    async with httpx.AsyncClient(headers=HEADERS, verify=False) as sess:
        resp = await sess.get(url)
        length = resp.headers.get("content-length")
        with open(out, "wb") as f:
            process = 0
            print(f"{info} {length}")
            for chunk in resp.iter_bytes(1024):
                f.write(chunk)

async def download_video(bvid):
    # 实例化 Video 类
    v = video.Video(bvid=bvid)
    # 获取视频下载链接
    download_url_data = await v.get_download_url(0)
    # 解析视频下载信息
    detecter = video.VideoDownloadURLDataDetecter(data=download_url_data)
    streams = detecter.detect_best_streams(
        video_max_quality=video.VideoQuality._720P,
        audio_max_quality=video.AudioQuality._192K,
        codecs=[video.VideoCodecs.AVC, video.VideoCodecs.HEV, video.VideoCodecs.AV1],
    )
    # 有 MP4 流 / FLV 流两种可能
    if detecter.check_flv_stream() == True:
        # FLV 流下载
        await download_url(streams[0].url, "视频/flv_temp.flv", "FLV 音视频流")
        # 转换文件格式
        os.system(f"{FFMPEG_PATH} -i 视频/flv_temp.flv 视频/{bvid}.mp4")
        # 删除临时文件
        os.remove("视频/flv_temp.flv")
    else:
        # MP4 流下载
        await download_url(streams[0].url, "视频/video_temp.m4s", "视频流")
        await download_url(streams[1].url, "视频/audio_temp.m4s", "音频流")
        # 混流
        os.system(
            f"{FFMPEG_PATH} -i 视频/video_temp.m4s -i 视频/audio_temp.m4s -vcodec copy -acodec copy 视频/{bvid}.mp4"
        )
        # 删除临时文件
        os.remove("视频/video_temp.m4s")
        os.remove("视频/audio_temp.m4s")

    print(f"已下载为：视频/{bvid}.mp4")

async def download_thumbnail(bvid):
    v = video.Video(bvid=bvid)
    info = await v.get_info()
    image_url = info["pic"]

    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
    else:
        print("图片下载失败，状态码：", response.status_code)
        exit()

    if image.width / image.height > 16 / 9:
        left = image.width / 2 - image.height / 9 * 8
        right = image.width / 2 + image.height / 9 * 8
        top = 0
        bottom = image.height
    else:
        top = image.height / 2 - image.width / 32 * 9
        bottom = image.height / 2 + image.width / 32 * 9
        left = 0
        right = image.width

    cropped_image = image.crop((left, top, right, bottom))
    resized_image = cropped_image.resize((352, 199))

    resized_image.save("封面/" + bvid + ".png", "PNG")
    print("已保存：", bvid)


async def download_thumbnail_special(bvid):
    v = video.Video(bvid=bvid)
    info = await v.get_info()
    image_url = info["pic"]

    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))

        # 4比3裁剪
        if image.width / image.height > 4 / 3:
            left = image.width / 2 - image.height / 3 * 2
            right = image.width / 2 + image.height / 3 * 2
            top = 0
            bottom = image.height
        else:
            top = image.height / 2 - image.width / 8 * 3
            bottom = image.height / 2 + image.width / 8 * 3
            left = 0
            right = image.width

        cropped_image = image.crop((left, top, right, bottom))
        resized_image = cropped_image.resize((1920, 1440))
        resized_image.save("其他图片/最高新曲封面4比3.png", "PNG")

        # 16比9裁剪
        if image.width / image.height > 16 / 9:
            left = image.width / 2 - image.height / 9 * 8
            right = image.width / 2 + image.height / 9 * 8
            top = 0
            bottom = image.height
        else:
            top = image.height / 2 - image.width / 32 * 9
            bottom = image.height / 2 + image.width / 32 * 9
            left = 0
            right = image.width

        cropped_image = image.crop((left, top, right, bottom))
        resized_image = cropped_image.resize((1920, 1080))
        resized_image.save("其他图片/最高新曲封面16比9.png", "PNG")

    else:
        print("图片下载失败，状态码：", response.status_code)
        exit()


class RankingMaker:
    def __init__(self, mode):
        self.mode = mode


        if mode == "daily" or mode == "daily-text":
            self.folder = "日刊/"
            total_phase = (today - datetime(year=2024, month=7, day=2)).days

            metadata = {
                "full_date": today.strftime("%Y.%m.%d"),
                "year": today.year,
                "month": today.month,
                "day": today.day,
                "weekday": today.weekday() + 1,
                "theme": themes[(today.weekday() + 1) % 7],
                "total_phase": total_phase,
                "phase": total_phase,
                "time_range": f"{today.strftime('%Y.%m.%d')} 00:00 —— {(today + timedelta(days=1)).strftime('%Y.%m.%d')} 00:00"  
            }
            with open("日刊/基本配置.yaml", "r", encoding="utf-8") as file:
                settings = yaml.safe_load(file)
                self.main = settings["main"]
                self.extend = settings["extend"]
                self.new = settings["new"]
            self.file_before = (
                today.strftime("%Y%m%d")
                + "与"
                + (today - timedelta(days=1)).strftime("%Y%m%d")
                + ".xlsx"
            )
            self.file_today = (
                (today + timedelta(days=1)).strftime("%Y%m%d")
                + "与"
                + today.strftime("%Y%m%d")
                + ".xlsx"
            )

            self.file_new = (
                "新曲榜"
                + (today + timedelta(days=1)).strftime("%Y%m%d")
                + "与"
                + today.strftime("%Y%m%d")
                + ".xlsx"
            )
            self.file_new_before = (
                "新曲榜"
                + today.strftime("%Y%m%d")
                + "与"
                + (today - timedelta(days=1)).strftime("%Y%m%d")
                + ".xlsx"
            )
        elif mode == "weekly":
            self.folder = "周刊/"
            total_phase = (now - datetime(2024,8,31)).days // 7

            metadata = {
                "full_date": now.strftime("%Y.%m.%d"),
                "year": now.year,
                "month": now.month,
                "day": now.day,
                "weekday": now.weekday() + 1,
                "theme": themes[(now.weekday() + 1) % 7],
                "total_phase": total_phase,
                "phase": total_phase,
                "time_range": f"{(now - timedelta(days=7)).strftime('%Y.%m.%d')} 00:00 —— {now.strftime('%Y.%m.%d')} 00:00"  
            }
            with open("周刊/基本配置.yaml", "r", encoding="utf-8") as file:
                settings = yaml.safe_load(file)
                self.main = settings["main"]
                self.extend = settings["extend"]
                self.new = settings["new"]
            with open("周刊/配置.yaml", "r", encoding="utf-8") as file:
                self.preferences = yaml.safe_load(file)[full_date]

            self.file_before = (
                (now - timedelta(days=7)).strftime("%Y-%m-%d")
                + ".xlsx"
            )
            self.file_today = (
                now.strftime("%Y-%m-%d")
                + ".xlsx"
            )

            self.file_new = (
                "新曲"
                + now.strftime("%Y-%m-%d")
                + ".xlsx"
            )
            self.file_new_before = (
                "新曲"
                + (now - timedelta(days=7)).strftime("%Y-%m-%d")
                + ".xlsx"
            )
        elif mode == "monthly":
            self.folder = "月刊/"
            total_phase = ( now.year - 2024)*12 + now.month - 6

            metadata = {
                "full_date": today.strftime("%Y.%m.%d"),
                "year": today.year,
                "month": today.month,
                "day": today.day,
                "weekday": today.weekday() + 1,
                "theme": themes[(today.weekday() + 1) % 7],
                "total_phase": total_phase,
                "phase": total_phase,
                "time_range": f"{(today - timedelta(days=today.day-1)).strftime('%Y.%m.%d')} 00:00 —— {(today + timedelta(days=1)).strftime('%Y.%m.%d')} 00:00"  
            }
            with open("月刊/基本配置.yaml", "r", encoding="utf-8") as file:
                settings = yaml.safe_load(file)
                self.main = settings["main"]
                self.extend = settings["extend"]
                self.new = settings["new"]
            with open("月刊/配置.yaml", "r", encoding="utf-8") as file:
                self.preferences = yaml.safe_load(file)[full_date]

            self.file_before = (
                (today - timedelta(days=today.day)).strftime("%Y-%m")
                + ".xlsx"
            )
            self.file_today = (
                today.strftime("%Y-%m")
                + ".xlsx"
            )

            self.file_new = (
                "新曲"
                + (today - timedelta(days=today.day)).strftime("%Y-%m")
                + ".xlsx"
            )
            self.file_new_before = (
                "新曲"
                + today.strftime("%Y-%m")
                + ".xlsx"
            )


        self.songs_data_today = pd.read_excel(self.folder + "数据/" + self.file_today, dtype={"pubdate": str})
        self.songs_data_today["pic"] = self.songs_data_today["bvid"] + ".png"
        self.songs_data_before = pd.read_excel(self.folder + "数据/" + self.file_before, dtype={"pubdate": str})
        self.songs_data_new = pd.read_excel(self.folder + "数据/" + self.file_new, dtype={"pubdate": str}, nrows=self.new)
        self.songs_data_new_before = pd.read_excel(
            self.folder + "数据/" + self.file_new_before, dtype={"pubdate": str}, nrows=self.new
        )

        if mode in ('daily', 'weekly','monthly'):
            with open(self.folder + '配置.yaml', "r", encoding="utf-8") as file:
                preferences = yaml.safe_load(file)[full_date]
            source_folder = r"D:\Music\VOCALOID传说曲"
            source_file = preferences["ED_filename"] + ".mp3"

            source_path = os.path.join(source_folder, source_file)
            destination_file = "BGM/副榜.mp3"
            destination_path = os.path.join(os.getcwd(), destination_file)
            shutil.copyfile(source_path, destination_path)
            metadata["OP_bvid"] = self.songs_data_before.at[0, "bvid"]
            metadata["OP_title"] = self.songs_data_before.at[0, "title"]
            metadata["OP_author"] = self.songs_data_before.at[0, "author"]
        
            metadata["ED_title"] = preferences["ED_title"]
        with open("基本信息数据.json", "w", encoding="utf-8") as file:
            json.dump(metadata, file, ensure_ascii=False, indent=4)



    def make_statistics_today(self):
        def high_points():
            if self.mode in ('daily', 'daily-text'):
                counts = {'10w':0, '2w':0,'1w':0}
                points_today = songs_data_today['point']
                for i in range(len(points_today)):
                    if points_today[i] >= 100000:
                        counts['10w'] += 1
                    if points_today[i] >= 20000:
                        counts['2w'] += 1
                    if points_today[i] >= 10000:
                        counts["1w"] += 1
            elif self.mode == 'weekly':
                counts = {'50w':0, '10w':0,'5w':0}
                points_today = songs_data_today['point']
                for i in range(len(points_today)):
                    if points_today[i] >= 500000:
                        counts['50w'] += 1
                    if points_today[i] >= 100000:
                        counts['10w'] += 1
                    if points_today[i] >= 50000:
                        counts["5w"] += 1
            elif self.mode == 'monthly':
                counts = {'100w':0, '50w':0,'10w':0}
                points_today = songs_data_today['point']
                for i in range(len(points_today)):
                    if points_today[i] >= 1000000:
                        counts['100w'] += 1
                    if points_today[i] >= 500000:
                        counts['50w'] += 1
                    if points_today[i] >= 100000:
                        counts["10w"] += 1
            return counts

        def start_points():
            return {
                'main': int(songs_data_today.at[self.main-1,'point']),
                'extend': int(songs_data_today.at[self.extend-1, 'point']),
                'new': int(songs_data_new.at[self.new-1,'point'])
            }

        def new_songs():
            if self.mode in ('daily','daily-text'):
                start_time = today - timedelta(days=4)
            elif self.mode == 'weekly':
                start_time = today - timedelta(days=13)
            elif self.mode == 'monthly':
                start_time = today.replace(day=1)
            counts = {'main':0, 'extend':0}
            for i in range(self.extend):
                pubdate = songs_data_today.at[i, 'pubdate']
                if datetime.strptime(pubdate,  "%Y-%m-%d %H:%M:%S") >= start_time:
                    if i<self.main:
                        counts['main'] += 1
                    counts['extend'] += 1
            return counts


        def count_names(key):
            with open("排除歌手.yaml",'r',encoding='utf-8') as file:
                removed_vocals = yaml.safe_load(file)
            counts = {}
            for names in songs_data_today[key]:
                for name in names.split('、'):
                    counts[name] = counts.get(name, 0) + 1
            

            counts = [{"name":k, "count":v} for (k,v) in counts.items() if k not in removed_vocals]
            counts = sorted(counts, key = lambda item: item["count"], reverse=True)
            
            #计算排名

            rank=1
            prev_value = None
            prev_rank = None

            for i in range(len(counts)):
                value = counts[i]["count"]
                rank = i+1
                if value != prev_value:
                    counts[i]['rank'] = rank
                    prev_rank = rank
                else:
                    counts[i]['rank'] = prev_rank
                prev_value = value
            
            
            counts = tuple(counts)
            return counts

        def output_counts():
            if self.mode in ('daily', 'daily-text'):
                file_path = f"统计/{today.strftime('%Y%m%d')}.json"
            elif self.mode == 'weekly':
                file_path = f"统计/{today.strftime('%Y-%m-%d')}.json"
            elif self.mode == 'monthly':
                file_path = f"统计/{today.strftime('%Y-%m')}.json"
            with open(self.folder + file_path,'w',encoding='utf-8') as file:
                json.dump(counts, file, ensure_ascii=False, indent=4)
    
        songs_data_today = self.songs_data_today
        songs_data_new = self.songs_data_new
        counts = {'high_points':high_points() , 'start_points':start_points() ,'new_songs': new_songs(), 'top_vocals': count_names('vocal'),'top_synthesizers': count_names('synthesizer')}
        output_counts()
        return counts

        
    def make_statistics(self):
        def compare(dict1, dict2):
            diff = {}
            for key in ['high_points','start_points','new_songs']:

                sub_dict1 = dict1[key]
                sub_dict2 = dict2[key]

                diff[key] = {}

                for sub_key in sub_dict1:
                    diff[key][sub_key] = {'today': sub_dict1[sub_key], 'before':sub_dict2[sub_key], 'change': sub_dict1[sub_key] - sub_dict2[sub_key]}
            
            for key in ['top_vocals','top_synthesizers']:

                sub_dict1 = dict1[key]
                diff[key] = []
                p=0
                q=0
                while q < len(sub_dict1) and sub_dict1[q]['rank']<=11:
                    if sub_dict1[p]['rank'] < sub_dict1[q]['rank']:
                        while p<q:
                            diff[key].append(sub_dict1[p])
                            p+=1
                    q+=1
                    
                sub_dict2 = dict2[key]
                for i in range(len(diff[key])):
                    for item in sub_dict2:
                        if item['name'] == diff[key][i]['name']:
                            diff[key][i]['change'] = sub_dict1[i]['count'] - item['count']
                            break
                    else:
                        diff[key][i]['count_change'] = sub_dict1[i]['count']


            return diff

        def read_statistics_before():
            if self.mode in ('daily', 'daily-text'):
                file_path = f'统计/{(today - timedelta(days=1)).strftime("%Y%m%d")}.json'
            elif self.mode == 'weekly':
                file_path = f'统计/{(today - timedelta(days=7)).strftime("%Y-%m-%d")}.json'
            elif self.mode == 'monthly':
                file_path = f'统计/{(today - timedelta(days=today.day)).strftime("%Y-%m")}.json'
            with open(self.folder + file_path, 'r', encoding='utf-8') as file:
                statistics_before = json.load(file)
            return statistics_before
        
        statistics_today = self.make_statistics_today()
        statistics_before = read_statistics_before()
        statistics = compare(statistics_today, statistics_before)
        
        with open('统计.json','w',encoding='utf-8') as file:
            json.dump(statistics, file, ensure_ascii=False, indent=4)

    def insert_clip_points(self, songs_data, main):
        songs_data["inPoint"] = "0"
        songs_data["outPoint"] = "0"
        for i in range(main):
            for clip in clip_points:
                if songs_data.at[i, "bvid"] == clip["bvid"]:
                    songs_data.at[i, "inPoint"] = clip["inPoint"]
                    songs_data.at[i, "outPoint"] = clip["outPoint"]
                    break


    def insert_before(self):
        if self.mode in ('daily','daily-text'):
            start_time = today
        elif self.mode == 'weekly':
            start_time = today - timedelta(days=6)
        elif self.mode == 'monthly':
            start_mode = today.replace(day=1)
        songs_data_today = self.songs_data_today
        songs_data_before = self.songs_data_before
        
        songs_data_today["rank_before"] = "--"
        songs_data_today["point_before"] = "--"
        songs_data_today["change"] = "new"

        for i in songs_data_today.index:
            song_data_before = songs_data_before[
                songs_data_before["name"] == songs_data_today.at[i, "name"]
            ]

            if not song_data_before.empty:
                song_data_before = song_data_before.iloc[0]
                rank_before = song_data_before["rank"]
                songs_data_today.at[i, "rank_before"] = song_data_before["rank"]
                songs_data_today.at[i, "point_before"] = song_data_before["point"]

                if rank_before < i + 1:
                    songs_data_today.at[i, "change"] = "down"
                elif rank_before == i + 1:
                    songs_data_today.at[i, "change"] = "cont"
                elif rank_before > i + 1:
                    songs_data_today.at[i, "change"] = "up"
            else:
                if (
                    datetime.strptime(
                        songs_data_today.at[i, "pubdate"], "%Y-%m-%d %H:%M:%S"
                    )
                    < start_time
                ):
                    songs_data_today.at[i, "rank_before"] = "--"
                    songs_data_today.at[i, "point_before"] = "--"
                    songs_data_today.at[i, "change"] = "up"


    def local_videos(self):

        def delete_videos(days, today_videos):
            file_path = f"视频/{(today - timedelta(days=days)).strftime('%Y%m%d')}下载视频.json"
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    old_videos = json.load(file)
                for old_video in old_videos:
                    if old_video not in today_videos and os.path.exists(
                        f"视频/{old_video}.mp4"
                    ):
                        os.remove(f"视频/{old_video}.mp4")

        
        downloaded_videos = os.listdir("./视频")
        songs_data_today = self.songs_data_today
        songs_data_new = self.songs_data_new

        today_videos = []
        for i in range(self.main):
            bvid = songs_data_today.at[i, "bvid"]
            today_videos.append(bvid)
        
        delete_videos(7, today_videos)


        file_path = f"视频/{today.strftime('%Y%m%d')}下载视频.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                download_list = json.load(file)
        else:
            download_list = []

        # 找下载新曲视频
        for i in range(self.new):
            bvid = songs_data_new.at[i, "bvid"]
            if bvid + ".mp4" not in downloaded_videos and bvid not in download_list:
                download_list.append(bvid)

        # 找下载主榜视频
        for i in range(self.main):
            bvid = songs_data_today.at[i, "bvid"]
            if bvid + ".mp4" not in downloaded_videos and bvid not in download_list:
                download_list.append(bvid)




        file_path = f"视频/{today.strftime('%Y%m%d')}下载视频.json"
        with open(file_path, "w") as file:
            json.dump(download_list, file, ensure_ascii=False, indent=4)

        total = len(download_list)
        for i in range(total):
            bvid = download_list[i]
            if bvid + ".mp4" not in downloaded_videos:
                asyncio.run(download_video(bvid=bvid))
                print(f"下载进度：{i+1}/{total}")

        print("现在清您去截取片段")



    def detect_language(character):
        code = ord(character)
        if (0x4E00 <= code <= 0x9FFF) or (0x3400 <= code <= 0x4DBF):
            return "Chinese"
        elif (
            (0xAC00 <= code <= 0xD7AF)
            or (0x1100 <= code <= 0x11FF)
            or (0x3130 <= code <= 0x318F)
        ):
            return "Korean"
        elif (
            (0x3040 <= code <= 0x309F)
            or (0x30A0 <= code <= 0x30FF)
            or (0xFF00 <= code <= 0xFFEF)
        ):
            return "Japanese"
        elif (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A):
            return "English"
        else:
            return "Other"

    def top_count(counts, number):
        top_tuple = sorted(counts.items(), key=lambda item: item[1], reverse=True)
        top_tuple = tuple((k,v) for (k,v) in top_tuple if v>1)
        top_list = []
        rank = 0
        name = top_tuple[0][0]
        count = top_tuple[0][1]
        index = 1
        while rank<number:
            if index < len(top_tuple) and top_tuple[index][1] == count:
                name = name + '、' + top_tuple[index][0]
                
            elif index == len(top_tuple) :

                top_list.append({'name':name,'count':count})
                break
            else:

                top_list.append({'name':name,'count':count})
                rank += 1
                name = top_tuple[index][0]
                count =  top_tuple[index][1]
            index += 1
        return top_list


    def insert_main_rank(self):
        songs_data_new = self.songs_data_new
        songs_data_today = self.songs_data_today
        songs_data_new['main_rank'] = '--'
        for i in range(self.new):
            song_data_main = songs_data_today[songs_data_today['name'] == songs_data_new.at[i, 'name']]
            if not song_data_main.empty:
                main_rank = song_data_main.iloc[0]['rank']
                songs_data_new.at[i,'main_rank'] = main_rank

    def local_thumbnails(self):

        pics_filename = os.listdir("./封面")
        pics_bvid = [pic[0:12] for pic in pics_filename]
        pics = {bvid: filename for bvid, filename in zip(pics_bvid, pics_filename)}

        # 下载封面
        for i in range(self.extend):
            bvid = self.songs_data_today.at[i, "bvid"]
            if bvid not in pics.keys():
                asyncio.run(download_thumbnail(bvid))

    def cover_thumbnail(self):
        if self.mode in ('daily', 'daily-text'):

            thumbnail_bvid = self.songs_data_new.at[0, "bvid"]
        elif self.mode == 'weekly':
            songs_data_today = self.songs_data_today
            for i in songs_data_today.index:
                if songs_data_today.at[i, 'change'] == 'new':
                    thumbnail_bvid = songs_data_today.at[i, 'bvid']
                    break
        
        asyncio.run(download_thumbnail_special(thumbnail_bvid))


    def make_resources(self):

        self.insert_main_rank()
        self.songs_data_today = self.songs_data_today.head(self.extend)
        self.insert_before()
        self.make_statistics()
        self.cover_thumbnail()
        self.local_thumbnails()
        print("现在可以开始制作图片")

        if self.mode != 'daily-text':
            self.local_videos()
            self.insert_clip_points(self.songs_data_today, self.main)
            self.insert_clip_points(self.songs_data_new, self.new)


        self.songs_data_today.to_json("数据.json", force_ascii=False, orient="records", indent=4)
        self.songs_data_new.to_json("新曲数据.json", force_ascii=False, orient="records", indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose the mode to run the program")
    parser.add_argument("--mode", choices=['daily','daily-text','weekly','monthly'],required=True, help="Select the mode: daily, weekly or monthly")

    args = parser.parse_args()

    ranking = RankingMaker(args.mode)
    ranking.make_resources()