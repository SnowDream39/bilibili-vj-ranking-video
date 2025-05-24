import yaml
import json
import pandas as pd
from datetime import datetime, timedelta

today = datetime(2024,12,30)

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
        # 读取排除名单
        with open("排除歌手.yaml", 'r', encoding='utf-8') as file:
            removed_vocals = yaml.safe_load(file)

        # 确保数据框中的名字列和分数列存在
        if key not in songs_data_today.columns or 'point' not in songs_data_today.columns:
            raise ValueError("数据框中缺少必要的列")

        # 分割名字并展平
        songs_data_today['names'] = songs_data_today[key].dropna().str.strip().str.split('、')
        names_df = songs_data_today.explode('names')

        # 计算每个名字的总分
        total_point = names_df.groupby('names')['point'].sum().reset_index()
        total_point.columns = ['name', 'point']

        # 过滤掉需要排除的名字
        total_point = total_point[~total_point['name'].isin(removed_vocals)]

        # 排序并计算排名
        total_point = total_point.sort_values(by='point', ascending=False)
        total_point['rank'] = total_point['point'].rank(method='dense', ascending=False).astype(int)

        # 返回结果
        return total_point.to_dict(orient='records')



    counts = {'high_points':high_points() , 'start_points':start_points() ,'new_songs': new_songs(), 'top_vocals': names_total_point('vocal'),'top_synthesizers': names_total_point('synthesizer')}
    with open(f"日刊/排名用统计/{today.strftime('%Y%m%d')}.json",'w',encoding='utf-8') as file:
        json.dump(counts, file, ensure_ascii=False, indent=4)
    return counts



while(today < datetime.today() - timedelta(1)):
    print(today)
    songs_data_today =  pd.read_excel(f"日刊/数据/{(today + timedelta(days=1)).strftime('%Y%m%d')}与{today.strftime('%Y%m%d')}.xlsx", dtype={'author':str, 'pubdate':str}, usecols=['name','author','uploader','synthesizer','vocal','rank','view','pubdate','point'])
    if today < datetime(2024,9,5):
        songs_data_new =  pd.read_excel(f"日刊/数据/新曲{(today + timedelta(days=1)).strftime('%Y%m%d')}与新曲{today.strftime('%Y%m%d')}.xlsx",nrows=10)
    else:
        songs_data_new =  pd.read_excel(f"日刊/数据/新曲榜{(today + timedelta(days=1)).strftime('%Y%m%d')}与{today.strftime('%Y%m%d')}.xlsx",nrows=10)

    statistics_today()

    today += timedelta(days=1)