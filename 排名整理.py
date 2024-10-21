import pandas as pd
from datetime import datetime, timedelta

songs = pd.read_excel('收录曲目.xlsx')
index = songs['Title'].values
allrank = pd.DataFrame(index=index, columns = ['count'])
allrank['count'] = 0
del songs,index

today = datetime(2024,7,3)
phase = 1
while today < datetime.now() - timedelta(1):
    file_name = f"日刊/数据/{(today + timedelta(days=1)).strftime('%Y%m%d')}与{today.strftime('%Y%m%d')}.xlsx"
    data = pd.read_excel(file_name)
    allrank[phase] = None
    for i in data.index:
        song = data.at[i,'name']
        if song in allrank.index:
            allrank.at[song, phase] = i+1
            if i<20:
                allrank.at[song,'count'] += 1
    phase += 1
    today += timedelta(days=1)
    print(phase)

allrank.to_excel('日刊排名整理草稿.xlsx')