import pandas as pd
import json
from datetime import datetime, timedelta
import yaml
import os
import shutil
import argparse
from typing import List
from abc import ABC, abstractmethod

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

# 封面下载功能已移至 下载封面.py
# 网络获取URL功能已移除，统一使用数据文件中的image_url
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
def json_find(data, key, value):
    for i in range(len(data)):
        if data[i][key] == value:
            return data[i]
    return None

class RankingMaker(ABC):
    folder: str
    metadata: dict
    preferences: dict
    file_today: str
    file_before: str
    file_new: str
    file_new_before: str

    def __init__(self, now: datetime) -> None:
        self.make_date(now)
        self.statistic_new_days = 5
        self.main, self.extend, self.new = 20, 100, 10
        self.before_start_time = now
        self.high_point_levels = [1e5,2e4,1e4]
        self.statistic_file_path = os.path.join('日刊', "新版统计", f"{self.today.strftime('%Y%m%d')}.json")
        self.statistic_before_path = os.path.join('日刊', "新版统计", f"{(self.today - timedelta(1)).strftime('%Y%m%d')}.json")
        self.prepare()


    # 以下是需要在子类实现的方法

    @abstractmethod
    def prepare(self) -> None:
        pass

    def make_date(self, now):
        self.now = now.replace(hour=0, minute=0, second=0, microsecond=0)
        self.today = self.now - timedelta(days=1)
        self.full_date = self.today.strftime("%Y.%m.%d")
    def make_audio(self):
        with open(self.folder + '配置.yaml', "r", encoding="utf-8") as file:
            preferences = yaml.safe_load(file)[self.full_date]
        self.metadata["ED_title"] = self.preferences["ED_title"]
        source_folder = r"D:\Music\VOCALOID传说曲"
        source_file = preferences["ED_filename"] + ".mp3"

        source_path = os.path.join(source_folder, source_file)
        destination_file = "BGM/副榜.mp3"
        destination_path = os.path.join(os.getcwd(), destination_file)
        shutil.copyfile(source_path, destination_path)
    def get_normal_datas(self):
        self.songs_data_today = pd.read_excel(os.path.join(self.folder, "数据", self.file_today), dtype={"author":str, "vocal":str, "pubdate": str, "rank": int})
        self.songs_data_today["pic"] = self.songs_data_today["bvid"] + ".png"
        self.songs_data_before = pd.read_excel(os.path.join(self.folder, "数据", self.file_before), dtype={"author":str,"vocal":str, "pubdate": str})
        self.songs_data_new = pd.read_excel(os.path.join(self.folder, "数据", self.file_new), dtype={"author":str,"vocal":str, "pubdate": str}, nrows=self.new)
        self.songs_data_new_before = pd.read_excel( os.path.join(self.folder, "数据", self.file_new_before), dtype={"author":str,"vocal":str, "pubdate": str}, nrows=self.new)

        self.metadata["OP_bvid"] = self.songs_data_before.at[0, "bvid"]
        self.metadata["OP_title"] = self.songs_data_before.at[0, "title"]
        self.metadata["OP_author"] = self.songs_data_before.at[0, "author"]
    
        self.today_pics = {}
    def output_metadata(self):

        with open("基本信息数据.json", "w", encoding="utf-8") as file:
            json.dump(self.metadata, file, ensure_ascii=False, indent=4)
    def make_statistics_today(self):
        def high_points():
            level_names = [f"{int(level//1e4)}w" for level in self.high_point_levels]
            counts = {k:0 for k in level_names}
            points_today = songs_data_today['point']
            for i in range(len(points_today)):
                if points_today[i] >= self.high_point_levels[0]:
                    counts[level_names[0]] += 1
                if points_today[i] >= self.high_point_levels[1]:
                    counts[level_names[1]] += 1
                if points_today[i] >= self.high_point_levels[2]:
                    counts[level_names[2]] += 1
                
            return counts
        
        def start_points():
            return {
                'main': int(songs_data_today.at[self.main-1,'point']),
                'extend': int(songs_data_today.at[self.extend-1, 'point']),
                'new': int(songs_data_new.at[self.new-1,'point'])
            }

        def new_songs():
            counts = {'main':0, 'extend':0}
            for i in range(self.extend):
                pubdate = songs_data_today.at[i, 'pubdate']
                if datetime.strptime(pubdate,  "%Y-%m-%d %H:%M:%S") >= (
                    self.today - timedelta(days=self.statistic_new_days-1)
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
        with open(self.statistic_file_path,'w',encoding='utf-8') as file:
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
            with open(self.statistic_before_path, 'r', encoding='utf-8') as file:
                statistics_before = json.load(file)
            return statistics_before

        def check_portraits(vocals: List[str]) -> None:
            for vocal in vocals:
                if not os.path.exists(f'头像/{vocal}.png'):
                    print(f'歌手头像 {vocal}.png 缺失')
    
        statistics_today = self.make_statistics_today()
        statistics_before = read_statistics_before()
        statistics = compare(statistics_today, statistics_before)
        check_portraits(list(map(lambda x: x['name'], statistics["top_vocals"]))[:10])
        
        with open('统计.json','w',encoding='utf-8') as file:
            json.dump(statistics, file, ensure_ascii=False, indent=4)
    def insert_clip_points(self, datas):
        miss_clip_points = []
        for songs_data, contain in datas:
            songs_data["inPoint"] = "0"
            songs_data["outPoint"] = "0"
            for i in range(contain):
                bvid = songs_data.at[i, "bvid"] 
                for clip in clip_points:
                    if bvid == clip["bvid"]:
                        songs_data.at[i, "inPoint"] = clip["inPoint"]
                        songs_data.at[i, "outPoint"] = clip["outPoint"]
                        break
                else:
                    print(f"缺少截取片段：{songs_data.at[i,'name']}({songs_data.at[i,'bvid']})")
                    miss_clip_points.append(bvid)
            with open("缺少截取片段视频.json",'w',encoding='utf-8') as file:
                json.dump(miss_clip_points, file, indent=4, ensure_ascii=False)
    def insert_before(self):
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
                rank = songs_data_today.at[i, "rank"]
                if rank_before < rank:
                    songs_data_today.at[i, "change"] = "down"
                elif rank_before == rank:
                    songs_data_today.at[i, "change"] = "cont"
                elif rank_before > rank:
                    songs_data_today.at[i, "change"] = "up"
            else:
                if (
                    datetime.strptime(
                        songs_data_today.at[i, "pubdate"], "%Y-%m-%d %H:%M:%S"
                    )
                    < self.before_start_time
                ):
                    songs_data_today.at[i, "rank_before"] = "--"
                    songs_data_today.at[i, "point_before"] = "--"
                    songs_data_today.at[i, "change"] = "up"
    def local_videos(self):
        
        downloaded_videos = list(map(lambda x: x.split('.')[0], os.listdir("./视频")))


        songs_data_today = self.songs_data_today.head(self.main)
        songs_data_new = self.songs_data_new.head(self.new)
        rank_videos = list(set(songs_data_today["bvid"].to_list()).union(set(songs_data_new["bvid"].to_list())))


        videos_to_download = list(set(rank_videos) - set(downloaded_videos))


        with open("urls.txt", "w", encoding="utf-8") as file:
            for video in videos_to_download:
                file.write(f"https://www.bilibili.com/video/{video}" + "\n")


    @staticmethod
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
    def local_thumbnails(self):

        local_pics = os.listdir("./封面")

        # 收集需要下载封面的视频BV号和URL
        for i in range(self.extend):
            bvid = self.songs_data_today.at[i, 'bvid']
            if bvid + '.png' not in local_pics:
                image_url = self.songs_data_today.at[i, 'image_url']
                if len(image_url) == 0:
                    print(f"警告：{bvid} 缺少image_url，跳过下载")
                    continue
                self.today_pics[bvid] = image_url
        
        with open('新增封面.json', 'w', encoding='utf-8') as file:
            json.dump(self.today_pics, file, indent=4, ensure_ascii=False)
        
        print(f"已输出 {len(self.today_pics)} 个需要下载封面的视频BV号到 新增封面.json")
        print("请运行 'python 下载封面.py' 来下载这些封面")
    def insert_vocal_colors(self):
        '''
        对songs_data_today操作
        '''
        with open("歌手代表色.json", 'r', encoding='utf-8') as file:
            vocal_colors = json.load(file)
        with open("排除歌手.yaml",'r',encoding='utf-8') as file:
            removed_vocals = yaml.safe_load(file)
        songs_data = self.songs_data_today
        songs_data['vocal_colors'] = [[] for _ in songs_data.index]
        for i in songs_data.index:
            if pd.notna(songs_data.at[i, 'vocal']):
                for vocal in songs_data.at[i, 'vocal'].split('、'):
                    vocal = vocal.strip()
                    color = json_find(vocal_colors, 1, vocal)
                    if color:
                        songs_data.at[i, 'vocal_colors'].append(color[0])
                    else:
                        songs_data.at[i, 'vocal_colors'].append('777777')
                        if vocal not in removed_vocals:
                            print(f"缺少歌手代表色：{vocal}")
            else:
                songs_data.at[i, 'vocal_colors'].append('777777')
                print(f"{songs_data.at[i, 'rank']}位 {songs_data.at[i, 'name']}({songs_data.at[i, 'bvid']})没打标")
    def make_fixes(self, songs_datas: List[pd.DataFrame]):
        for songs_data in songs_datas:
            if 'fixA' in songs_data.columns:
                songs_data['coin'] = songs_data['coin'].astype(str)
                songs_data['fix'] = songs_data['fixB'] * songs_data['fixC']
                songs_data['fix'].apply(lambda x:f"{x:.2f}")
            else:
                songs_data['fixA'] = 1.0
                songs_data['fix'] = 1.0
    def output_songs_data(self):
        self.songs_data_today.to_json("数据.json", force_ascii=False, orient="records", indent=4)
        self.songs_data_new.to_json("新曲数据.json", force_ascii=False, orient="records", indent=4)

class DailyTextMaker(RankingMaker):
    def prepare(self):
        self.folder = "日刊/"

        self.today = self.now - timedelta(days=1)
        total_phase = (self.today - datetime(year=2024, month=7, day=2)).days

        full_date = self.now.strftime("%Y.%m.%d")
        self.metadata = {
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
        self.file_before = ( self.today.strftime("%Y%m%d") + "与" + (self.today - timedelta(days=1)).strftime("%Y%m%d") + ".xlsx")
        self.file_today = ( (self.today + timedelta(days=1)).strftime("%Y%m%d") + "与" + self.today.strftime("%Y%m%d") + ".xlsx")
        self.file_new = ( "新曲榜" + (self.today + timedelta(days=1)).strftime("%Y%m%d") + "与" + self.today.strftime("%Y%m%d") + ".xlsx")
        self.file_new_before = ( "新曲榜" + self.today.strftime("%Y%m%d") + "与" + (self.today - timedelta(days=1)).strftime("%Y%m%d") + ".xlsx")

        self.high_point_levels = [1e5,2e4,1e4]
        self.statistic_file_path = os.path.join(self.folder, "新版统计", f"{self.today.strftime('%Y%m%d')}.json")
        self.statistic_before_path = os.path.join(self.folder, "新版统计", f"{(self.today - timedelta(days=1)).strftime('%Y%m%d')}.json")
        self.before_start_time = self.today
    def cover_thumbnail(self):
        thumbnail_url = self.songs_data_new.at[0, 'image_url']
        # 输出特殊封面信息到JSON文件
        with open('特殊封面.json', 'w', encoding='utf-8') as file:
            json.dump({'special_thumbnail_url': thumbnail_url}, file, indent=4, ensure_ascii=False)
        print("已输出特殊封面信息到 特殊封面.json")
        print("请运行 'python 下载封面.py' 来下载特殊封面")         
    def make_resources(self):
        self.get_normal_datas()
        self.make_statistics()
        self.insert_main_rank()
        self.songs_data_today = self.songs_data_today.head(self.extend)
        self.insert_vocal_colors()
        self.insert_before()
        self.make_fixes([self.songs_data_today, self.songs_data_new])
        self.output_metadata()
        self.cover_thumbnail()
        self.local_thumbnails()
        self.output_songs_data() 

class WeeklyRankingMaker(RankingMaker):
    def prepare(self):
        self.folder = "周刊/"
        
        self.today = self.now - timedelta(days=(self.now.weekday()-4)%7)
        total_phase = (self.today - datetime(2024,8,30)).days // 7
        full_date = self.today.strftime("%Y.%m.%d")
        self.metadata = {
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

        self.file_before = ( (self.today - timedelta(days=6)).strftime("%Y-%m-%d") + ".xlsx")
        self.file_today = ( (self.today + timedelta(1)).strftime("%Y-%m-%d") + ".xlsx")
        self.file_new = ( "新曲" + (self.today + timedelta(1)).strftime("%Y-%m-%d") + ".xlsx")
        self.file_new_before = ( "新曲" + (self.today - timedelta(days=6)).strftime("%Y-%m-%d") + ".xlsx")

        self.high_point_levels = [5e5,1e5,5e4]
        self.million_data = pd.read_excel("周刊/数据/百万记录"+(self.today + timedelta(days=1)).strftime("%Y-%m-%d")+".xlsx", dtype={"pubdate": str})
        self.achievement_data = pd.read_excel("周刊/数据/成就"+(self.today + timedelta(days=1)).strftime("%Y-%m-%d")+".xlsx", dtype={"pubdate": str})
        self.statistic_file_path = os.path.join(self.folder, "新版统计", f"{self.today.strftime('%Y-%m-%d')}.json")
        self.statistic_before_path = os.path.join(self.folder, "新版统计", f"{(self.today - timedelta(days=7)).strftime('%Y-%m-%d')}.json")
        self.history_file = pd.read_excel(os.path.join(self.folder, '数据', f"历史{(self.today + timedelta(days=1)).strftime('%Y-%m-%d')}.xlsx"))
        self.before_start_time = self.today - timedelta(6)
        self.statistic_new_days = 14
    def insert_seperate(self):
        daily_files = {}
        for i in range(7,0,-1):
            print(f'正在读取第{8-i}天数据')
            file_path = os.path.join("数据",f"{(self.today - timedelta(i-2)).strftime('%Y%m%d')}与{(self.today - timedelta(i-1)).strftime('%Y%m%d')}.xlsx")
            daily_files[i] = pd.read_excel("日刊/" + file_path, usecols=['name','rank']).set_index('name')

        for items in ((self.songs_data_today, self.main), (self.songs_data_new, self.new)):
            songs_data = items[0]
            songs_data['daily_ranks'] = [[] for _ in range(len(songs_data))]
            song_names = songs_data['name'].to_list()
            for i in range(7,0,-1):
                
                print(f"正在插入第{8-i}天排名")
                songs_data_daily = daily_files[i]
                daily_ranks = []

                for song_name in song_names:
                    if song_name in songs_data_daily.index:
                        daily_ranks.append(songs_data_daily.at[song_name, 'rank'])
                    else:
                        daily_ranks.append("--")

                songs_data['daily_ranks'] = songs_data['daily_ranks'].apply(lambda x: x + [daily_ranks.pop(0)])
    def million_reach(self):
        million_data = self.million_data
        for i in million_data.index:
            song_record = self.songs_data_today[self.songs_data_today['bvid'] == million_data.at[i, 'bvid']]
            if (song_record.empty):
                # 如果在今日数据中找不到，使用百万记录数据中的image_url
                image_url = million_data.at[i, 'image_url'] if 'image_url' in million_data.columns else ""
                if len(image_url) == 0:
                    print(f"警告：百万记录 {million_data.at[i, 'bvid']} 缺少image_url，跳过")
                    continue
                self.today_pics[million_data.at[i, 'bvid']] = image_url
            else:
                self.today_pics[million_data.at[i, 'bvid']] = self.songs_data_today[self.songs_data_today['bvid'] == million_data.at[i, 'bvid']].iloc[0]['image_url']
        million_data.to_json("百万达成.json", orient='records', force_ascii=False, indent=4)
    def history(self):
        history_file = self.history_file
        with open("历史数据.json", "w", encoding="utf-8") as f:
            json.dump(history_file.to_dict(orient='records'), f, ensure_ascii=False, indent=4)

    def achievements(self):
        data = self.achievement_data
        for i in data.index:
            song_record = self.songs_data_today[self.songs_data_today['bvid'] == data.at[i, 'bvid']]
            if (song_record.empty):
                # 如果在今日数据中找不到，使用成就数据中的image_url
                image_url = data.at[i, 'image_url'] if 'image_url' in data.columns else ""
                if len(image_url) == 0:
                    print(f"警告：成就记录 {data.at[i, 'bvid']} 缺少image_url，跳过")
                    continue
                self.today_pics[data.at[i, 'bvid']] = image_url
            else:
                self.today_pics[data.at[i, 'bvid']] = self.songs_data_today[self.songs_data_today['bvid'] == data.at[i, 'bvid']].iloc[0]['image_url']
        data.to_json("成就.json", orient='records', force_ascii=False, indent=4)
    def cover_thumbnail(self):
        """
        选择主榜内上榜次数最少的歌曲作为封面。
        """
        songs_data_today = self.songs_data_today
        if self.preferences.get("thumbnail", False):
            thumbnail_bvid: str = self.preferences["thumbnail"]
            thumbnail_url = songs_data_today.loc[songs_data_today['bvid'] == thumbnail_bvid, 'image_url'].values[0]
        else:
            sort_by_count = songs_data_today.head(20).sort_values("count", ascending=True)
            thumbnail_url = sort_by_count.iloc[0]['image_url']
        # 输出特殊封面信息到JSON文件
        with open('特殊封面.json', 'w', encoding='utf-8') as file:
            json.dump({'special_thumbnail_url': thumbnail_url}, file, indent=4, ensure_ascii=False)
        print("已输出特殊封面信息到 特殊封面.json")
        print("请运行 'python 下载封面.py' 来下载特殊封面")
    def make_resources(self):
        self.make_audio()
        self.get_normal_datas()
        self.make_statistics()
        self.insert_main_rank()
        self.insert_seperate()
        self.million_reach()
        self.history()
        self.achievements()
        self.songs_data_today = self.songs_data_today.head(self.extend)
        self.insert_vocal_colors()
        self.insert_before()
        self.make_fixes([self.songs_data_today, self.songs_data_new])
        self.output_metadata()
        self.cover_thumbnail()
        self.local_thumbnails()
        self.local_videos()
        self.insert_clip_points([[self.songs_data_today, self.main],
                                [self.songs_data_new, self.new]])
        self.output_songs_data() 

class MonthlyRankingMaker(RankingMaker):
    def prepare(self):
        self.folder = "月刊/"

        self.today = self.now.replace(day=1) - timedelta(days=1)
        total_phase = ( self.today.year - 2024)*12 + self.today.month - 6

        full_date = self.today.strftime("%Y.%m.%d")
        self.metadata = {
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

        self.file_before = ( (self.today - timedelta(days=self.today.day)).strftime("%Y-%m") + ".xlsx")
        self.file_today = ( self.today.strftime("%Y-%m") + ".xlsx")
        self.file_new_before = ( "新曲" + (self.today - timedelta(days=self.today.day)).strftime("%Y-%m") + ".xlsx") 
        self.file_new = ( "新曲" + self.today.strftime("%Y-%m") + ".xlsx")

        self.high_point_levels = [1e6,5e5,1e5]
        self.statistic_file_path = os.path.join(self.folder, "新版统计", f"{self.today.strftime('%Y-%m')}.json")
        self.statistic_before_path = os.path.join(self.folder, "新版统计", f"{(self.today - timedelta(days=self.today.day)).strftime('%Y-%m')}.json")
        self.before_start_time = self.today.replace(day=1)
        self.statistic_new_days = self.today.day
    def insert_seperate(self):
        weekly_files = {}
        for i in range(4,-1,-1):
            weekly_today = self.today + timedelta(1)
            date = weekly_today - timedelta((weekly_today.weekday() - 5)%7 + i * 7)
            print(f"正在读取{date.strftime('%Y%m%d')}排名")
            file_path = os.path.join("数据",f"{date.strftime('%Y-%m-%d')}.xlsx")
            weekly_files[i] = pd.read_excel("周刊/" + file_path, usecols=['name','rank']).set_index('name')
            
        for items in ((self.songs_data_today, self.main), (self.songs_data_new, self.new)):
            songs_data = items[0]
            songs_data['daily_ranks'] = [[] for _ in songs_data.index]
            for i in range(4,-1,-1):
                print(f"正在插入第{5-i}周排名")

                songs_data_daily = weekly_files[i]

                for j in songs_data.index:
                    song_name = songs_data.at[j, 'name']
                    if song_name in songs_data_daily.index:    
                        songs_data.at[j, 'daily_ranks'].append(songs_data_daily.at[song_name, 'rank'])
                    else:
                        songs_data.at[j, 'daily_ranks'].append("--")
    
    def make_resources(self):
        self.make_audio()
        self.get_normal_datas()
        self.make_statistics()
        self.insert_main_rank()
        self.insert_seperate()
        self.songs_data_today = self.songs_data_today.head(self.extend)
        self.insert_vocal_colors()
        self.insert_before()
        self.make_fixes([self.songs_data_today, self.songs_data_new])
        self.output_metadata()
        self.local_thumbnails()
        self.local_videos()
        self.insert_clip_points([[self.songs_data_today, self.main],
                                [self.songs_data_new, self.new]])
        self.output_songs_data() 


class MonthReviewMaker(RankingMaker):
    def prepare(self):
        with open("基本信息数据.json","w", encoding="utf-8") as file:
            metadata = {
                "title": "每日冠军回顾"
            }
            json.dump(metadata, file, indent=4, ensure_ascii=False)

        last_day_of_last_month = self.today
        first_day_of_last_month = last_day_of_last_month.replace(day=1)
        current_day = first_day_of_last_month
        all_columns = ['title','bvid','name','author','uploader','copyright','synthesizer','vocal','type','pubdate','duration','page','view','favorite','coin','like','viewR','favoriteR','coinR','likeR','fixA','fixB','fixC','point']
        top_datas = pd.DataFrame(columns=all_columns)
        while current_day <= last_day_of_last_month:

            filename = "日刊/数据/"+ (current_day + timedelta(days=1)).strftime("%Y%m%d")+"与"+current_day.strftime("%Y%m%d")+".xlsx"
            current_song_data = pd.read_excel(filename,nrows=1,dtype={"pubdate": str})
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
        self.songs_data = top_datas
        self.make_resources() 

    def local_videos(self):
        """
        会保存每天新增视频的文件。具体逻辑还没想好。
        """
        def delete_videos(days):
            file_path = os.path.join("视频", f"{(self.today - timedelta(days=days)).strftime('%Y%m%d')}视频.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    old_videos = json.load(file)
                for old_video in old_videos:
                    if old_video not in rank_videos and os.path.exists(
                        f"视频/{old_video}.mp4"
                    ):
                        os.remove(f"视频/{old_video}.mp4")

        
        downloaded_videos = os.listdir("./视频")

        songs_data = self.songs_data
        rank_videos = songs_data["bvid"].to_list()

        rank_videos = list(map(lambda x:x + ".mp4", rank_videos))
        videos_to_download = list(set(rank_videos) - set(downloaded_videos))
        
        file_path = os.path.join("视频",f"{self.today.strftime('%Y%m%d')}视频.json")

        with open(file_path, "w") as file:
            json.dump(rank_videos, file, ensure_ascii=False, indent=4)

        # 输出视频下载列表，不执行实际下载
        if videos_to_download:
            print(f"发现 {len(videos_to_download)} 个需要下载的视频")
            print("请使用其他下载工具下载以下视频：")
            for video_bvid in videos_to_download:
                print(f"  https://www.bilibili.com/video/{video_bvid}")

    def make_resources(self):
        self.songs_data.to_json("月回顾数据.json", force_ascii=False, orient="records", indent=4)
        self.songs_data.to_excel("月回顾数据.xlsx", index=False)
        self.local_videos()

class SpecialRankingMaker(RankingMaker):
    def prepare(self):
        with open(os.path.join("特刊","基本配置.yaml"), encoding='utf-8') as file:
            settings = yaml.safe_load(file)
            self.special_name = settings['special_name']
            self.contain = settings['contain']
            self.title = settings['title']
        with open(os.path.join("特刊","配置.yaml"), encoding='utf-8') as file:
            preferences = yaml.safe_load(file)
            if preferences and self.special_name in preferences:
                self.contain = settings['contain']
        with open("基本信息数据.json","w", encoding="utf-8") as file:
            self.metadata = {
                "special_name": self.special_name,
                "title": self.title
            }
            json.dump(self.metadata, file, indent=4, ensure_ascii=False)
        self.songs_data = pd.read_excel(os.path.join("特刊","数据", f"{self.special_name}.xlsx"))

    def local_videos(self):
        
        downloaded_videos = list(map(lambda x: x.split('.')[0], os.listdir("./视频")))


        rank_videos = self.songs_data["bvid"].to_list()


        videos_to_download = list(set(rank_videos) - set(downloaded_videos))
        
        file_path = os.path.join("视频",f"{self.today.strftime('%Y%m%d')}视频.json")

        with open(file_path, "w") as file:
            json.dump(rank_videos, file, ensure_ascii=False, indent=4)

        with open("urls.txt", "w", encoding="utf-8") as file:
            for video in videos_to_download:
                file.write(f"https://www.bilibili.com/video/{video}" + "\n")

        print("现在清您去截取片段")
  
    def make_resources(self):
        self.songs_data = self.songs_data.head(self.contain)
        self.make_fixes([self.songs_data])

        self.local_videos()
        self.insert_clip_points([[self.songs_data, self.contain]])
        self.songs_data.to_json("数据.json", force_ascii=False, orient="records", indent=4)
        self.output_metadata()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose the mode to run the program")
    parser.add_argument("--mode", choices=['daily','daily-text','weekly','monthly','month-review','special'],required=True, help="Select the mode: daily, weekly, monthly or special")

    args = parser.parse_args()
    now = datetime.now()
    if args.mode == 'daily-text':
        ranking = DailyTextMaker(now)
    elif args.mode == 'weekly':
        ranking = WeeklyRankingMaker(now)
    elif args.mode == 'monthly':
        ranking = MonthlyRankingMaker(now)
    elif args.mode == 'month-review':
        ranking = MonthReviewMaker(now)
    elif args.mode == 'special':
        ranking = SpecialRankingMaker(now)
    
    ranking.make_resources()