import yaml
import json
import pandas as pd
from datetime import datetime, timedelta


def statistics_today():


    def names_total_point(key):
        with open("排除歌手.yaml",'r',encoding='utf-8') as file:
            removed_vocals = yaml.safe_load(file)
        total_point = {}
        for i in songs_data_today.index:
            names = songs_data_today.at[i,key]
            if pd.notna(names):
                for name in names.strip().split('、'):
                    if name in total_point:
                        total_point[name] = total_point[name] + int(songs_data_today.at[i,'point'])
                    else:
                        total_point[name] = int(songs_data_today.at[i, 'point'])
        if key == 'vocal':
            total_point = [{"name":k, "point":v} for (k,v) in total_point.items() if k not in removed_vocals]
        else:
            total_point = [{"name":k, "point":v} for (k,v) in total_point.items()]
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


        total_point = tuple(total_point)
        return total_point



    counts = { 'top_authors': names_total_point('author')}
    with open(f"日刊/P主测试统计/{today.strftime('%Y%m%d')}.json",'w',encoding='utf-8') as file:
        json.dump(counts, file, ensure_ascii=False, indent=4)
    return counts


today = datetime(2025,7,21)

while(today < datetime(2025,7,28)):
    print(today)
    songs_data_today =  pd.read_excel(f"日刊/数据/{(today + timedelta(days=1)).strftime('%Y%m%d')}与{today.strftime('%Y%m%d')}.xlsx", dtype={'author':str, 'pubdate':str})
    statistics_today()

    today += timedelta(days=1)