import json
from bilibili_api import Credential, Picture, dynamic
import yaml
import asyncio

def make_text():
    text = "日刊虚拟歌手外语排行榜动态版（测试）\n新曲榜"

    with open("新曲数据.json",'r',encoding='utf-8') as file:
        songs_data_new = json.load(file)

    for i in range(9,-1,-1):
        song_data = songs_data_new[i]
        text += f"\n{song_data['rank']} 【{song_data['vocal']}{' cover' if song_data['type'] == '翻唱' else ''}】{song_data['name']}【{song_data['author']}】 {song_data['point']}分 {song_data['bvid']}"

    with open("日刊极简版.txt", 'w', encoding='utf-8') as file:
        file.write(text)

    return text

def make_pics():
    pics = [Picture.from_file(f"简易主榜图片/{i}.png") for i in range(1,11)]
    pics.extend([Picture.from_file("其他图片/统计歌手.png"), Picture.from_file("其他图片/统计数据.png")])
    return pics

async def main():

    with open("账号验证.yaml") as file:
        data = yaml.safe_load(file)
        cred = Credential(sessdata=data['sessdata'], bili_jct=data['bili_jct'])

    text = make_text()
    pics = make_pics()
    dyn = dynamic.BuildDynamic.create_by_args(text=text, pics=pics)
    r = await dynamic.send_dynamic(dyn, credential=cred)
    print(r)

if __name__ == "__main__":
    asyncio.run(main())