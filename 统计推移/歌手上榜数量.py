import pandas as pd
from datetime import datetime, timedelta
import json

data = pd.DataFrame(columns=['name','type','value','date'])

today = datetime(2024,7,20)

while today < datetime(2024,9,20):
    print(today.strftime("%Y-%m-%d"))
    file_path = f"日刊/统计/{today.strftime('%Y%m%d')}.json"
    with open(file_path, encoding='utf-8') as file:
        data_today = json.load(file)['top_vocals']
    for name_data in data_today:
        song_data = {'name':name_data['name'],
                     'value':name_data['count'],
                     'date':today.strftime("%Y-%m-%d")}
        data = data._append(song_data, ignore_index=True)
    
    today += timedelta(days=1)


data['type'] = data['name']
data.to_csv("统计推移/歌手上榜数量.csv", encoding='utf-8', index=False)