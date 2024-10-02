import pandas as pd
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
from math import ceil, floor

contain = 20
extend = 100
new = 10

SESSDATA = "c17c6918%2C1735996419%2Ca5015%2A72CjArPmcRcNPy0x_fO4fdMqtFjEqdZ-F6tKqMOF5IWEmdxlP5MLT6-o8nSc5YZledGV4SVnlKWlRmT2NhNEgtU2J3VWZ1OG9LRkZJbFN3a056ZjhrRm9SckdQWWFIbl9hUURfMUxtXzFpZXFoN29KRHdHeC1aQTU3b3RBT1F1RFlFVEtZTnpKTkpnIIEC"
BILI_JCT = "4c9f3874cdcc31ae90931826dee881e4"
BUVID3 = "421282EF-A860-65A1-218B-83A1EC3EA78A31062infoc"
AC_TIME_VALUE = "98d89026646ab79e213bfa5195bbff72"
FFMPEG_PATH = "D:/Tool/ffmpeg-2024-07-07-git-0619138639-full_build/bin/ffmpeg.exe"

credential = Credential(
    sessdata=SESSDATA, bili_jct=BILI_JCT, buvid3=BUVID3, ac_time_value=AC_TIME_VALUE
)

try:
    if sync(credential.check_refresh()):
        sync(credential.refresh())
except:
    pass


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
    v = video.Video(bvid=bvid, credential=credential)
    # 获取视频下载链接
    download_url_data = await v.get_download_url(0)
    # 解析视频下载信息
    detecter = video.VideoDownloadURLDataDetecter(data=download_url_data)
    streams = detecter.detect_best_streams(video_max_quality=video.VideoQuality._1080P,audio_max_quality=video.AudioQuality._192K, codecs=[video.VideoCodecs.AVC, video.VideoCodecs.HEV, video.VideoCodecs.AV1])
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
            f'{FFMPEG_PATH} -i 视频/video_temp.m4s -i 视频/audio_temp.m4s -vcodec copy -acodec copy 视频/{bvid}.mp4'
        )
        # 删除临时文件
        os.remove("视频/video_temp.m4s")
        os.remove("视频/audio_temp.m4s")

    print(f"已下载为：视频/{bvid}.mp4")


def insert_clip_points(songs_data, clip_points, contain):
    songs_data["inPoint"] = "0"
    songs_data["outPoint"] = "0"
    for i in range(contain):
        for clip in clip_points:
            if songs_data.at[i, "bvid"] == clip["bvid"]:
                songs_data.at[i, "inPoint"] = clip["inPoint"]
                songs_data.at[i, "outPoint"] = clip["outPoint"]
                break


def insert_before(songs_data_today, songs_data_before):
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
                < today
            ):
                songs_data_today.at[i, "rank_before"] = "--"
                songs_data_today.at[i, "point_before"] = "--"
                songs_data_today.at[i, "change"] = "up"


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


def delete_videos(days):
    file_path = f"视频/{(today - timedelta(days=2)).strftime('%Y%m%d')}下载视频.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            old_videos = json.load(file)
        for old_video in old_videos:
            if old_video not in today_videos and os.path.exists(
                f"视频/{old_video}.mp4"
            ):
                os.remove(f"视频/{old_video}.mp4")


def update_algorithm(current_song_data):
    if current_song_data.at[0,'copyright'] == 0:
        current_song_data.at[0,'copyright'] = 2
    view = current_song_data.at[0,"view"]
    favorite = current_song_data.at[0,"favorite"]
    coin = current_song_data.at[0,"coin"]
    like = current_song_data.at[0,"like"]
    copyright = current_song_data.at[0,"copyright"]
    viewR = 0 if view == 0 else max(ceil(min(max((coin + favorite), 0) * 20 / view, 1) * 100) / 100, 0)
    favoriteR = 0 if favorite <= 0 else max(ceil(min(max(favorite + 2 * coin, 0) * 10 / (favorite * 20 + view) * 40, 20) * 100) / 100, 0)
    coinR = 0 if (1 if copyright in [1, 3] else 2) * coin * 40 + view == 0 else max(ceil(min(((1 if copyright in [1, 3] else 2) * coin * 40) / ((1 if copyright in [1, 3] else 2) * coin * 40 + view) * 80, 40) * 100) / 100, 0)
    likeR = 0 if like <= 0 else max(floor(max(coin + favorite, 0) / (like * 20 + view) * 100 * 100) / 100, 0)
    current_song_data['viewR'] = viewR
    current_song_data['favoriteR'] = favoriteR
    current_song_data['coinR'] = coinR
    current_song_data['likeR'] = likeR
    current_song_data['point'] = int(view * viewR + favorite * favoriteR + coin * coinR + like * likeR) 

today = datetime.today()
last_day_of_last_month = datetime(today.year,  today.month, 1)- timedelta(days=1)
first_day_of_last_month = last_day_of_last_month.replace(day=1)
current_day = first_day_of_last_month
all_columns = ['title','bvid','name','author','uploader','copyright','synthesizer','vocal','type','pubdate','duration','view','favorite','coin','like','viewR','favoriteR','coinR','likeR','point']
top_datas = pd.DataFrame(columns=all_columns)

while current_day <= last_day_of_last_month:
    filename = "日刊/数据/"+ (current_day + timedelta(days=1)).strftime("%Y%m%d")+"与"+current_day.strftime("%Y%m%d")+".xlsx"
    current_song_data = pd.read_excel(filename,nrows=1,dtype={"pubdate": str})
    if current_day < datetime(2024,7,12):
        update_algorithm(current_song_data)
    current_song_data = current_song_data[all_columns]
    top_datas = pd.concat([top_datas, current_song_data],ignore_index=True)
    current_day += timedelta(days=1)

top_datas['day'] = top_datas.index + 1
top_datas['view_rank'] = top_datas['view'].rank(ascending=False,method='min').astype(int)
top_datas['favorite_rank'] = top_datas['favorite'].rank(ascending=False,method='min').astype(int)
top_datas['coin_rank'] = top_datas['coin'].rank(ascending=False,method='min').astype(int)
top_datas['like_rank'] = top_datas['like'].rank(ascending=False,method='min').astype(int)

top_datas.to_excel("月回顾数据.xlsx",index=False)
top_datas.to_json("月回顾数据.json", force_ascii=False, orient="records", indent=4)

# 下载视频
downloaded_videos = os.listdir("./视频")
download_list = []
for bvid in top_datas["bvid"]:
    if bvid + ".mp4" not in downloaded_videos and bvid + ".mp4" not in download_list:
        download_list.append(bvid)

file_path = f"视频/月下载视频.json"
with open(file_path, "w") as file:
    json.dump(download_list, file, ensure_ascii=False, indent=4)

total = len(download_list)
for i in range(total):
    bvid = download_list[i]
    if bvid + ".mp4" not in downloaded_videos:
        asyncio.get_event_loop().run_until_complete(download_video(bvid=bvid))
        print(f"下载进度：{i+1}/{total}")