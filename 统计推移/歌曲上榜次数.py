import pandas as pd
from datetime import datetime, timedelta

data = pd.DataFrame(columns=['name','type','value','date'])

today = datetime(2024,8,20)

while today < datetime(2024,9,20):
    print(today.strftime("%Y-%m-%d"))
    file_path = f"日刊/数据/{today.strftime('%Y%m%d')}与{(today-timedelta(days=1)).strftime('%Y%m%d')}.xlsx"
    songs_data_today = pd.read_excel(file_path).sort_values("count",ascending=False,ignore_index=True).head(20)
    for i in range(20):
        song_data = {'name':songs_data_today.at[i,'name'],
                     'value':songs_data_today.at[i,'count'],
                     'date':today.strftime("%Y-%m-%d")}
        data = data._append(song_data, ignore_index=True)
    
    today += timedelta(days=1)


data['type'] = data['name']
data.to_csv("统计推移/歌曲上榜次数.csv", encoding='utf-8', index=False)