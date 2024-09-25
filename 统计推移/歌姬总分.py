import pandas as pd
from datetime import datetime, timedelta
import json

data = pd.DataFrame(columns=['name','type','value','date'])

today = datetime(2024,7,20)

while today < datetime(2024,9,22):
    print(today.strftime("%Y-%m-%d"))
    file_path = f"日刊/新版统计/{today.strftime('%Y%m%d')}.json"
    with open(file_path, encoding='utf-8') as file:
        data_today = json.load(file)['top_vocals']
    i = 0
    while i<20 and i<(len(data_today)):
        name_data = data_today[i]
        song_data = {'name':name_data['name'],
                    'value':name_data['point'],
                    'date':today.strftime("%Y-%m-%d")}
        data = data._append(song_data, ignore_index=True)
        i += 1

    today += timedelta(days=1)


data['type'] = data['name']
data.to_csv("统计推移/歌姬总分.csv", encoding='utf-8', index=False)