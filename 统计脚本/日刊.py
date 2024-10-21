import yaml
import json
import pandas as pd
from datetime import datetime, timedelta


def statistics_today():
    def high_points():
        counts = {'10w':0, '2w':0,'1w':0}
        points_today = songs_data_today['point']
        for i in range(len(points_today)):
            if points_today[i] >= 100000:
                counts['10w'] += 1
            if points_today[i] >= 20000:
                counts['2w'] += 1
            if points_today[i] >= 10000:
                counts["1w"] += 1
        return counts
    
    def start_points():
        return {
            'main': int(songs_data_today.at[19,'point']),
            'extend': int(songs_data_today.at[99, 'point']),
            'new': int(songs_data_new.at[9,'point'])
        }

    def new_songs():
        counts = {'main':0, 'extend':0}
        for i in range(100):
            pubdate = songs_data_today.at[i, 'pubdate']
            if datetime.strptime(pubdate,  "%Y-%m-%d %H:%M:%S") >= (
                today - timedelta(days=4)
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



    counts = {'high_points':high_points() , 'start_points':start_points() ,'new_songs': new_songs(), 'top_vocals': names_total_point('vocal'),'top_synthesizers': names_total_point('synthesizer')}
    with open(f"日刊/新版统计/{today.strftime('%Y%m%d')}.json",'w',encoding='utf-8') as file:
        json.dump(counts, file, ensure_ascii=False, indent=4)
    return counts


today = datetime(2024,10,17)

while(today < datetime.today() - timedelta(1)):
    print(today)
    songs_data_today =  pd.read_excel(f"日刊/数据/{(today + timedelta(days=1)).strftime('%Y%m%d')}与{today.strftime('%Y%m%d')}.xlsx", dtype={'author':str, 'pubdate':str})
    if today < datetime(2024,9,5):
        songs_data_new =  pd.read_excel(f"日刊/数据/新曲{(today + timedelta(days=1)).strftime('%Y%m%d')}与新曲{today.strftime('%Y%m%d')}.xlsx",nrows=10)
    else:
        songs_data_new =  pd.read_excel(f"日刊/数据/新曲榜{(today + timedelta(days=1)).strftime('%Y%m%d')}与{today.strftime('%Y%m%d')}.xlsx",nrows=10)

    statistics_today()

    today += timedelta(days=1)