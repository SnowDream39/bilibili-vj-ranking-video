import pandas as pd
import json
import asyncio
from datetime import datetime, timedelta
from bilibili_api import video, HEADERS
import requests
from PIL import Image
from io import BytesIO
import httpx
import yaml
import os
import shutil
import argparse

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
        os.system(f"ffmpeg -i 视频/flv_temp.flv 视频/{bvid}.mp4")
        # 删除临时文件
        os.remove("视频/flv_temp.flv")
    else:
        # MP4 流下载
        await download_url(streams[0].url, "视频/video_temp.m4s", "视频流")
        await download_url(streams[1].url, "视频/audio_temp.m4s", "音频流")
        # 混流
        os.system(
            f"ffmpeg -i 视频/video_temp.m4s -i 视频/audio_temp.m4s -vcodec copy -acodec copy 视频/{bvid}.mp4"
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
    def __init__(self, now: datetime, mode: str):
        self.now = now.replace(hour=0, minute=0, second=0, microsecond=0)
        self.today = self.now - timedelta(days=1)
        full_date = self.today.strftime("%Y.%m.%d")
        self.mode = mode

        if mode == "daily" or mode == "daily-text":
            self.folder = "日刊/"

            self.today = self.now - timedelta(days=1)
            total_phase = (self.today - datetime(year=2024, month=7, day=2)).days

            full_date = self.now.strftime("%Y.%m.%d")
            metadata = {
                "full_date": full_date,
                "year": self.now.year,
                "month": self.today.month,
                "day": self.today.day,
                "weekday": self.today.weekday() + 1,
                "theme": themes[(self.today.weekday() + 1) % 7],
                "total_phase": total_phase,
                "phase": total_phase,
                "time_range": f"{self.today.strftime('%Y.%m.%d')} 00:00 —— {(self.today + timedelta(days=1)).strftime('%Y.%m.%d')} 00:00"  
            }
            with open("日刊/基本配置.yaml", "r", encoding="utf-8") as file:
                settings = yaml.safe_load(file)
                self.main = settings["main"]
                self.extend = settings["extend"]
                self.new = settings["new"]
            self.file_before = (
                self.today.strftime("%Y%m%d")
                + "与"
                + (self.today - timedelta(days=1)).strftime("%Y%m%d")
                + ".xlsx"
            )
            self.file_today = (
                (self.today + timedelta(days=1)).strftime("%Y%m%d")
                + "与"
                + self.today.strftime("%Y%m%d")
                + ".xlsx"
            )

            self.file_new = (
                "新曲榜"
                + (self.today + timedelta(days=1)).strftime("%Y%m%d")
                + "与"
                + self.today.strftime("%Y%m%d")
                + ".xlsx"
            )
            self.file_new_before = (
                "新曲榜"
                + self.today.strftime("%Y%m%d")
                + "与"
                + (self.today - timedelta(days=1)).strftime("%Y%m%d")
                + ".xlsx"
            )
        elif mode == "weekly":
            self.folder = "周刊/"
            
            self.today = self.now - timedelta(days=(self.now.weekday()-4)%7)
            total_phase = (self.today - datetime(2024,8,30)).days // 7
            full_date = self.today.strftime("%Y.%m.%d")
            metadata = {
                "full_date": (self.today + timedelta(1)).strftime("%Y.%m.%d"),
                "year": self.now.year,
                "month": self.now.month,
                "day": self.now.day,
                "weekday": self.now.weekday() + 1,
                "theme": themes[(self.now.weekday() + 1) % 7],
                "total_phase": total_phase,
                "phase": total_phase,
                "time_range": f"{(self.today - timedelta(days=6)).strftime('%Y.%m.%d')} 00:00 —— {(self.today + timedelta(1)).strftime('%Y.%m.%d')} 00:00"  
            }
            with open("周刊/基本配置.yaml", "r", encoding="utf-8") as file:
                settings = yaml.safe_load(file)
                self.main = settings["main"]
                self.extend = settings["extend"]
                self.new = settings["new"]
            with open("周刊/配置.yaml", "r", encoding="utf-8") as file:
                self.preferences = yaml.safe_load(file)[full_date]

            self.file_before = (
                (self.today - timedelta(days=6)).strftime("%Y-%m-%d")
                + ".xlsx"
            )
            self.file_today = (
                (self.today + timedelta(1)).strftime("%Y-%m-%d")
                + ".xlsx"
            )

            self.file_new = (
                "新曲"
                + (self.today + timedelta(1)).strftime("%Y-%m-%d")
                + ".xlsx"
            )
            self.file_new_before = (
                "新曲"
                + (self.today - timedelta(days=6)).strftime("%Y-%m-%d")
                + ".xlsx"
            )

            self.million_data = pd.read_excel("周刊/数据/百万记录"+(self.today + timedelta(days=1)).strftime("%Y-%m-%d")+".xlsx", dtype={"pubdate": str})
        elif mode == "monthly":
            self.folder = "月刊/"

            self.today = self.now.replace(day=1) - timedelta(days=1)
            total_phase = ( self.today.year - 2024)*12 + self.today.month - 6

            full_date = self.today.strftime("%Y.%m.%d")
            metadata = {
                "full_date": self.today.strftime("%Y.%m"),
                "year": self.now.year,
                "month": self.today.month,
                "day": self.today.day,
                "weekday": self.today.weekday() + 1,
                "theme": themes[(self.today.weekday() + 1) % 7],
                "total_phase": total_phase,
                "phase": total_phase,
                "time_range": f"{(self.today - timedelta(days=self.today.day-1)).strftime('%Y.%m.%d')} 00:00 —— {(self.today + timedelta(days=1)).strftime('%Y.%m.%d')} 00:00"  
            }
            with open("月刊/基本配置.yaml", "r", encoding="utf-8") as file:
                settings = yaml.safe_load(file)
                self.main = settings["main"]
                self.extend = settings["extend"]
                self.new = settings["new"]
            with open("月刊/配置.yaml", "r", encoding="utf-8") as file:
                self.preferences = yaml.safe_load(file)[full_date]

            self.file_before = (
                (self.today - timedelta(days=self.today.day)).strftime("%Y-%m")
                + ".xlsx"
            )
            self.file_today = (
                self.today.strftime("%Y-%m")
                + ".xlsx"
            )

            self.file_new_before = (
                "新曲"
                + (self.today - timedelta(days=self.today.day)).strftime("%Y-%m")
                + ".xlsx"
            )
            self.file_new = (
                "新曲"
                + self.today.strftime("%Y-%m")
                + ".xlsx"
            )


        self.songs_data_today = pd.read_excel(self.folder + "数据/" + self.file_today, dtype={"author":str, "vocal":str, "pubdate": str})
        self.songs_data_today["pic"] = self.songs_data_today["bvid"] + ".png"
        self.songs_data_before = pd.read_excel(self.folder + "数据/" + self.file_before, dtype={"author":str,"vocal":str, "pubdate": str})
        self.songs_data_new = pd.read_excel(self.folder + "数据/" + self.file_new, dtype={"author":str,"vocal":str, "pubdate": str}, nrows=self.new)
        self.songs_data_new_before = pd.read_excel(
            self.folder + "数据/" + self.file_new_before, dtype={"author":str,"vocal":str, "pubdate": str}, nrows=self.new
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
        self.today_pics = []

    def make_statistics_today(self):
        def high_points():
            if self.mode in ('daily', 'daily-text'):
                levels = [1e5,2e4,1e4]
            elif self.mode == 'weekly':
                levels = [5e5,1e5,5e4]
            elif self.mode == 'monthly':
                levels = [1e6,5e5,1e5]
            level_names = [f"{int(level//1e4)}w" for level in levels]
            counts = {k:0 for k in level_names}
            points_today = songs_data_today['point']
            for i in range(len(points_today)):
                if points_today[i] >= levels[0]:
                    counts[level_names[0]] += 1
                if points_today[i] >= levels[1]:
                    counts[level_names[1]] += 1
                if points_today[i] >= levels[2]:
                    counts[level_names[2]] += 1
                
            return counts
        
        def start_points():
            return {
                'main': int(songs_data_today.at[19,'point']),
                'extend': int(songs_data_today.at[99, 'point']),
                'new': int(songs_data_new.at[9,'point'])
            }

        def new_songs():
            counts = {'main':0, 'extend':0}
            if self.mode in ('daily', 'daily-text'):
                for i in range(100):
                    pubdate = songs_data_today.at[i, 'pubdate']
                    if datetime.strptime(pubdate,  "%Y-%m-%d %H:%M:%S") >= (
                        self.today - timedelta(days=4)
                    ):
                        if i<20:
                            counts['main'] += 1
                        counts['extend'] += 1
            elif self.mode == 'weekly':
                for i in range(100):
                    pubdate = songs_data_today.at[i, 'pubdate']
                    if datetime.strptime(pubdate,  "%Y-%m-%d %H:%M:%S") >= (
                        self.today - timedelta(days=13)
                    ):
                        if i<20:
                            counts['main'] += 1
                        counts['extend'] += 1
            if self.mode == 'monthly':
                for i in range(200):
                    pubdate = songs_data_today.at[i, 'pubdate']
                    if datetime.strptime(pubdate,  "%Y-%m-%d %H:%M:%S") >= (
                        self.today.replace(day=1)
                    ):
                        if i<20:
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

        def names_total_point(key):
            with open("排除歌手.yaml",'r',encoding='utf-8') as file:
                removed_vocals = yaml.safe_load(file)
            total_point = {}
            highest_song = {}
            for i in songs_data_today.index:
                names = songs_data_today.at[i,key]
                if pd.notna(names):
                    for name in names.strip().split('、'):
                        if name in highest_song:
                            total_point[name] = total_point[name] + int(songs_data_today.at[i,'point'])
                        else:
                            highest_song[name] = songs_data_today.at[i,'name']
                            if songs_data_today.at[i, 'type'] == '翻唱':
                                highest_song[name] += '(翻)'
                            total_point[name] = int(songs_data_today.at[i, 'point'])

            total_point = [{"name":k, "point":v} for (k,v) in total_point.items() if k not in removed_vocals]
            total_point = sorted(total_point, key = lambda item: item["point"], reverse=True)
            
            #计算排名

            rank=1
            prev_value = None
            prev_rank = None

            for i in range(len(total_point)):
                value = total_point[i]["point"]
                rank = i+1
                if value != prev_value:
                    total_point[i]['rank'] = rank
                    prev_rank = rank
                else:
                    total_point[i]['rank'] = prev_rank
                prev_value = value
            
            #插入最高歌曲

            for i in range(len(total_point)):
                name = total_point[i]['name']
                total_point[i]['highest_song'] = highest_song[name]


            total_point = tuple(total_point)
            return total_point



        songs_data_today = self.songs_data_today
        songs_data_new = self.songs_data_new
        counts = {'high_points':high_points() , 'start_points':start_points() ,'new_songs': new_songs(), 'top_vocals': names_total_point('vocal')}
        with open(f"日刊/新版统计/{self.today.strftime('%Y%m%d')}.json",'w',encoding='utf-8') as file:
            json.dump(counts, file, ensure_ascii=False, indent=4)
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
            
            for key in ['top_vocals']:

                diff[key] = dict1[key]
                sub_dict2 = dict2[key]
                for i in range(10):
                    for item in sub_dict2:
                        if item['name'] == diff[key][i]['name']:
                            diff[key][i]['rank_before'] = item['rank']
                            
                            if diff[key][i]['rank'] < item['rank']:
                                diff[key][i]['change'] = 'up'
                            elif diff[key][i]['rank'] == item['rank']:
                                diff[key][i]['change'] = 'cont'
                            elif diff[key][i]['rank'] > item['rank']:
                                diff[key][i]['change'] = 'down'
                            break
                    else:
                        diff[key][i]['rank_before'] = '--'
                        diff[key][i]['change'] = 'up'


            return diff

        def read_statistics_before():  #目前仅加入日刊统计补齐功能
            if self.mode in ('daily', 'daily-text'):
                file_path = f'新版统计/{(self.today - timedelta(days=1)).strftime("%Y%m%d")}.json'
            elif self.mode == 'weekly':
                file_path = f'新版统计/{(self.today - timedelta(days=7)).strftime("%Y-%m-%d")}.json'
            elif self.mode == 'monthly':
                file_path = f'新版统计/{(self.today - timedelta(days=self.today.day)).strftime("%Y-%m")}.json'
            if os.path.exists(self.folder + file_path):
                with open(self.folder + file_path, 'r', encoding='utf-8') as file:
                    statistics_before = json.load(file)
            else:
                if self.mode in ('daily', 'daily-text'):
                    temp_ranking_maker = RankingMaker(self.now - timedelta(days=1),'daily-text')
                    temp_ranking_maker.make_statistics()
                    statistics_before = read_statistics_before()
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
            else:
                print(f"缺少截取片段：{songs_data.at[i,'name']}({songs_data.at[i,'bvid']})")

    def insert_before(self):
        if self.mode in ('daily','daily-text'):
            start_time = self.today
        elif self.mode == 'weekly':
            start_time = self.today - timedelta(days=6)
        elif self.mode == 'monthly':
            start_time = self.today.replace(day=1)
        songs_data_today = self.songs_data_today
        songs_data_before = self.songs_data_before
        
        songs_data_today["rank_before"] = "--"
        songs_data_today["point_before"] = "--"
        songs_data_today["rate"] = "--"
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
                if song_data_before["point"] != 0:
                    songs_data_today.at[i, "rate"] = round(songs_data_today.at[i, "point"] / song_data_before["point"], 4) - 1

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
            file_path = f"视频/{(self.today - timedelta(days=days)).strftime('%Y%m%d')}下载视频.json"
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


        file_path = f"视频/{self.today.strftime('%Y%m%d')}下载视频.json"
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




        file_path = f"视频/{self.today.strftime('%Y%m%d')}下载视频.json"
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
                songs_data_new.at[i,'main_rank'] = int(main_rank)

    def insert_daily(self):
        for items in ((self.songs_data_today, self.main), (self.songs_data_new, self.new)):
            songs_data = items[0]
            songs_data['daily_ranks'] = [[] for _ in songs_data.index]
            for i in range(7,0,-1):
                print(f"正在插入第{8-i}天排名")
                file_path = f"数据/{(self.today - timedelta(i-2)).strftime('%Y%m%d')}与{(self.today - timedelta(i-1)).strftime('%Y%m%d')}.xlsx"
                songs_data_daily = pd.read_excel("日刊/" + file_path)
                songs_data_daily.set_index('name',inplace=True)

                for j in songs_data.index:
                    song_name = songs_data.at[j, 'name']
                    if song_name in songs_data_daily.index:    
                        songs_data.at[j, 'daily_ranks'].append(songs_data_daily.at[song_name, 'rank'])
                    else:
                        songs_data.at[j, 'daily_ranks'].append("--")

    def insert_weekly(self):
        for items in ((self.songs_data_today, self.main), (self.songs_data_new, self.new)):
            songs_data = items[0]
            songs_data['daily_ranks'] = [[] for _ in songs_data.index]
            for i in range(4,-1,-1):
                date = self.today - timedelta((self.today.weekday() - 5)%7 + i * 7)
                print(f"正在插入{date.strftime('%Y%m%d')}排名")
                file_path = f"数据/{date.strftime('%Y-%m-%d')}.xlsx"
                songs_data_daily = pd.read_excel("周刊/" + file_path)
                songs_data_daily.set_index('name',inplace=True)

                for j in songs_data.index:
                    song_name = songs_data.at[j, 'name']
                    if song_name in songs_data_daily.index:    
                        songs_data.at[j, 'daily_ranks'].append(songs_data_daily.at[song_name, 'rank'])
                    else:
                        songs_data.at[j, 'daily_ranks'].append("--")

    def local_thumbnails(self):

        local_pics = os.listdir("./封面")

        # 下载封面
        for i in range(self.extend):
            self.today_pics.append(self.songs_data_today.at[i, 'bvid'] + '.png')
        
        for pic in self.today_pics:
            if pic not in local_pics:
                asyncio.run(download_thumbnail(pic[0:12]))

    def cover_thumbnail(self):
        if self.mode in ('daily', 'daily-text'):

            thumbnail_bvid = self.songs_data_new.at[0, "bvid"]
        elif self.mode in ('weekly', 'monthly' ):
            songs_data_today = self.songs_data_today
            for i in songs_data_today.index:
                if songs_data_today.at[i, 'change'] == 'new':
                    thumbnail_bvid = songs_data_today.at[i, 'bvid']
                    break
        
        asyncio.run(download_thumbnail_special(thumbnail_bvid))

    def million_reach(self):
        million_data = self.million_data
        for i in million_data.index:
            self.today_pics.append(million_data.at[i, 'bvid'] + '.png')
        million_data.to_json("百万达成.json", orient='records', force_ascii=False, indent=4)

    def insert_vocal_colors(self):
        with open("歌姬代表色.json", 'r', encoding='utf-8') as file:
            vocal_colors = json.load(file)
        with open("排除歌手.yaml",'r',encoding='utf-8') as file:
            removed_vocals = yaml.safe_load(file)
        songs_data = self.songs_data_today
        songs_data['vocal_colors'] = [[] for _ in songs_data.index]
        for i in songs_data.index:
            if pd.notna(songs_data.at[i, 'vocal']):
                for vocal in songs_data.at[i, 'vocal'].split('、'):
                    if vocal in vocal_colors.keys():
                        songs_data.at[i, 'vocal_colors'].append(vocal_colors[vocal])
                    else:
                        songs_data.at[i, 'vocal_colors'].append('777777')
                        if vocal not in removed_vocals:
                            print(f"缺少歌手代表色：{vocal}")
            else:
                songs_data.at[i, 'vocal_colors'].append('777777')
                print(f"{songs_data.at[i, 'name']}({songs_data.at[i, 'bvid']})没打标")

    def make_resources(self):

        self.make_statistics()
        self.insert_main_rank()
        self.songs_data_today = self.songs_data_today.head(self.extend)
        self.insert_before()
        self.insert_vocal_colors()

        if self.mode == 'weekly':
            self.insert_daily()
            self.million_reach()
        elif self.mode == 'monthly':
            self.insert_weekly()

        if self.mode != 'daily-text':
            self.local_videos()
            self.insert_clip_points(self.songs_data_today, self.main)
            self.insert_clip_points(self.songs_data_new, self.new)


        self.cover_thumbnail()
        self.local_thumbnails()

        self.songs_data_today.to_json("数据.json", force_ascii=False, orient="records", indent=4)
        self.songs_data_new.to_json("新曲数据.json", force_ascii=False, orient="records", indent=4)

        print("现在可以开始制作图片")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose the mode to run the program")
    parser.add_argument("--mode", choices=['daily','daily-text','weekly','monthly'],required=True, help="Select the mode: daily, weekly or monthly")

    args = parser.parse_args()

    ranking = RankingMaker(datetime.now(),args.mode)
    ranking.make_resources()