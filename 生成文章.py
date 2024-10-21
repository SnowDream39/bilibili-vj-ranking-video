from bs4 import BeautifulSoup
import json

def new_tag(tag_name, text=None, **attributes):
    # 创建新标签
    tag = soup.new_tag(tag_name)
    
    # 处理所有属性
    for attr, value in attributes.items():
        if attr == 'class_':
            tag['class'] = value
        else:
            tag[attr] = value
    # 添加文本
    if text:
        tag.string = text
    
    # 返回标签
    return tag

with open("数据.json",'r', encoding='utf-8') as file:
    songs_data_today = json.load(file)
with open("新曲数据.json", 'r', encoding='utf-8') as file:
    songs_data_new = json.load(file)

# 创建一个空的 BeautifulSoup 对象
soup = BeautifulSoup(features="html.parser")

soup.append("""

### 收录规则
收录投稿于bilibili、使用虚拟歌手引擎调教创作的外语歌曲，原则上需投稿在VOCALOID·UTAU分区。
            
同时收录本家投稿和搬运，包括画质提升、字幕版等。
            
一首曲目的同一版本仅收录其中一个，优先使用本家投稿。
            
如果没有本家投稿，则以本期得分最高的一个搬运作为数据。
            
计算公式见视频版。

### 可能不收录的情况
二创PV、直接使用原曲歌声制作的remix、歌声合成软件演唱的比例小于一半、使用没有公开获取途径的音源、一个视频包含多曲

### 新曲榜
单独排名两日内投稿的新曲，且保证所有曲目排名均上升。
            
如果被搬运一段时间后本家投稿，在10日内未上过主榜的可以进入新曲榜。

![cut-off-5](https://i0.hdslb.com/bfs/article/4adb9255ada5b97061e610b682b8636764fe50ed.png)
"""
)


soup.append(BeautifulSoup(f"<strong><p class='font-size-23'>新曲榜</p></strong>", 'html.parser'))

for i in range(9,-1,-1):
    soup.append("\n\n")
    song_data = songs_data_new[i]
    song_box = soup.new_tag("div")
    song_box.append( BeautifulSoup(f"<strong><p class='font-size-20'>第{song_data['rank']}位\n</p></strong>", 'html.parser'))
    song_box.append(new_tag('div', f"\n\n![]({song_data['image_url']})"))
    song_box.append(new_tag("p", song_data['title']))
    song_box.append(new_tag("p", f"P主：{song_data['author']} {'本家投稿' if song_data['copyright'] == 1 else '搬运：' + song_data['uploader']} {song_data['type']}", class_ = "font-size-12"))
    song_box.append(new_tag("p", f"歌手：{song_data['vocal']}", class_ = "font-size-12"))
    song_box.append(new_tag("p", f"引擎：{song_data['synthesizer']}", class_='font-size-12'))
    song_box.append(new_tag("p", f"播放：{song_data['view']}（×{song_data['viewR']}） {song_data['view_rank']}位"))
    song_box.append(new_tag("p", f"收藏：{song_data['favorite']}（×{song_data['favoriteR']}） {song_data['favorite_rank']}位"))
    song_box.append(new_tag("p", f"硬币：{song_data['coin']}（×{song_data['coinR']}） {song_data['coin_rank']}位"))
    song_box.append(new_tag("p", f"点赞：{song_data['like']}（×{song_data['likeR']}） {song_data['like_rank']}位"))
    song_box.append(new_tag("p", f"得分：{song_data['point']}"))
    song_box.append(new_tag("p", f"总榜排名：{song_data['main_rank']}"))
    song_box.append(new_tag("p", f"链接：{song_data['bvid']}"))
    soup.append(song_box)

soup.append(BeautifulSoup(f"\n<strong><p class='font-size-23'>主榜</p></strong>\n", 'html.parser'))

html_output = str(soup)
with open("专栏文本.md", 'w', encoding='utf-8') as file:
    file.write(html_output)
