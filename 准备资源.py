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
    async with httpx.AsyncClient(headers=HEADERS) as sess:
        resp = await sess.get(url)
        length = resp.headers.get("content-length")
        with open(out, "wb") as f:
            process = 0
            for chunk in resp.iter_bytes(1024):
                if not chunk:
                    break

                process += len(chunk)
                print(f"下载 {info} {process} / {length}")
                f.write(chunk)


async def download_video(bvid):
    # 实例化 Video 类
    v = video.Video(bvid=bvid, credential=credential)
    # 获取视频下载链接
    download_url_data = await v.get_download_url(0)
    # 解析视频下载信息
    detecter = video.VideoDownloadURLDataDetecter(data=download_url_data)
    streams = detecter.detect_best_streams()
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
            f"{FFMPEG_PATH} -i 视频/video_temp.m4s -i 视频/audio_temp.m4s -c:v libx264 -c:a aac -strict experimental 视频/{bvid}.mp4"
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
        else:
            print(
                songs_data.at[i, "bvid"],
                songs_data.at[i, "name"],
                "截取片段缺失",
            )


def insert_before(songs_data_today, songs_data_before):
    songs_data_today["rank_before"] = "--"
    songs_data_today["point_before"] = "--"
    songs_data_today["change"] = "new"

    for i in songs_data_today.index:
        song_data_before = songs_data_before[
            songs_data_before["bvid"] == songs_data_today.at[i, "bvid"]
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
    resized_image = cropped_image.resize((391, 220))

    resized_image.save("封面/" + bvid + ".png", "PNG")
    print("已保存：", bvid)


async def download_thumbnail_special(bvid):
    v = video.Video(bvid=bvid)
    info = await v.get_info()
    image_url = info["pic"]

    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
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
        resized_image = cropped_image.resize((800, 600))

        resized_image.save("其他图片/最高新曲封面.png", "PNG")
    else:
        print("图片下载失败，状态码：", response.status_code)
        exit()

# 读取基本配置

with open('基本配置.yaml', 'r', encoding='utf-8') as file:
    settings = yaml.safe_load(file)
    contain = settings['contain']
    extend = settings['extend']
    new = settings['new']

today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
    days=1
)
metadata = {"date": today.strftime("%Y.%m.%d")}

# 副榜BGM
with open("BGM/副榜.yaml", 'r', encoding='utf-8') as file:
    bgm_data = yaml.safe_load(file)
source_folder = r"D:\Music\VOCALOID传说曲"
source_file =  bgm_data[metadata['date']]['filename'] + ".mp3"
metadata['ED_title'] = bgm_data[metadata['date']]['title']
source_path = os.path.join(source_folder, source_file)
destination_file = "BGM/副榜.mp3"
destination_path = os.path.join(os.getcwd(), destination_file)
shutil.copyfile(source_path, destination_path)


file_yesterday = (
    today.strftime("%Y%m%d")
    + "与"
    + (today - timedelta(days=1)).strftime("%Y%m%d")
    + ".xlsx"
)
file_today = (
    (today + timedelta(days=1)).strftime("%Y%m%d")
    + "与"
    + today.strftime("%Y%m%d")
    + ".xlsx"
)

file_new = (
    "新曲"
    + (today + timedelta(days=1)).strftime("%Y%m%d")
    + "与新曲"
    + today.strftime("%Y%m%d")
    + ".xlsx"
)

songs_data_today = pd.read_excel("数据/" + file_today, dtype={"pubdate": str})
songs_data_today = songs_data_today.head(extend)
songs_data_today["pic"] = songs_data_today["bvid"] + ".png"
songs_data_before = pd.read_excel("数据/" + file_yesterday, dtype={"pubdate": str})
songs_data_new = pd.read_excel("数据/" + file_new, dtype={"pubdate": str})
songs_data_new["rank"]
songs_data_new = songs_data_new.head(new)

metadata["OP_bvid"] = songs_data_before.at[0, "bvid"]
metadata["OP_title"] = songs_data_before.at[0, "title"]
metadata["OP_author"] = songs_data_before.at[0, "author"]

with open("截取片段.json", "r", encoding="utf-8") as file:
    clip_points = json.load(file)

downloaded_videos = os.listdir("./视频")
pics_filename = os.listdir("./封面")
pics_bvid = [pic[0:12] for pic in pics_filename]
pics = {bvid: filename for bvid, filename in zip(pics_bvid, pics_filename)}

download_list = []




# 增删本地视频

today_videos = []
for i in range(contain):
    bvid = songs_data_today.at[i, "bvid"]
    today_videos.append(bvid)
file_path = f"视频/{(today - timedelta(days=2)).strftime('%Y%m%d')}下载视频.json"
with open(file_path,'r') as file:
    old_videos = json.load(file)
for old_video in old_videos:
    if old_video not in today_videos and os.path.exists(f"视频/{old_video}.mp4"):
        os.remove(f"视频/{old_video}.mp4")



# 新曲
insert_clip_points(songs_data_new, clip_points, new)
for i in range(new):
    bvid = songs_data_new.at[i, "bvid"]
    if bvid + ".mp4" not in downloaded_videos:
        asyncio.get_event_loop().run_until_complete(download_video(bvid))
        download_list.append(bvid)

# 总榜
insert_before(songs_data_today, songs_data_before)
insert_clip_points(songs_data_today, clip_points, contain)
for i in range(contain):
    bvid = songs_data_today.at[i, "bvid"]
    if bvid + ".mp4" not in downloaded_videos:
        asyncio.get_event_loop().run_until_complete(download_video(bvid))
        download_list.append(bvid)
for i in range(extend):
    bvid = songs_data_today.at[i, "bvid"]
    if bvid not in pics.keys():
        asyncio.get_event_loop().run_until_complete(download_thumbnail(bvid))

# 最高新曲封面图片
bvid = songs_data_today[songs_data_today["change"] == "new"].iloc[0]["bvid"]
metadata["cover_thumbnail"] = bvid + ".png"
asyncio.get_event_loop().run_until_complete(download_thumbnail_special(bvid))

if download_list:
    with open(file_path, "a") as file:
        json.dump(download_list, file, indent=4)

with open("基本信息数据.json", "w", encoding="utf-8") as file:
    json.dump(metadata, file, ensure_ascii=False, indent=4)

print("现在清您去截取片段")

insert_clip_points(songs_data_new, clip_points, new)
insert_clip_points(songs_data_today, clip_points, contain)

songs_data_today.to_json("数据.json", force_ascii=False, orient="records", indent=4)
songs_data_new.to_json("新曲数据.json", force_ascii=False, orient="records", indent=4)
