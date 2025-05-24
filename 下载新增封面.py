'''
实在是很奇怪，真怎么就突然下载封面出错了呢？
而且是卡住了，谁也不知道怎么回事。
'''

import requests
from PIL import Image
from io import BytesIO
import asyncio
import json

async def download_thumbnail(bvid, image_url):
    print(f"正在下载封面：{bvid}")
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
    else:
        print("图片下载失败，状态码：", response.status_code)
        exit()

    if image.width / image.height > 16 / 9:
        left = image.width / 2 - image.height / 9 * 8
        right = image.width / 2 + image.height / 9 * 8
        top = 0
        bottom = image.height
    else:
        top = image.height / 2 - image.width / 32 * 9
        bottom = image.height / 2 + image.width / 32 * 9
        left = 0
        right = image.width

    cropped_image = image.crop((left, top, right, bottom))
    resized_image = cropped_image.resize((352, 199))

    resized_image.save("封面/" + bvid + ".png", "PNG")

if __name__ == '__main__':
    with open('新增封面.json') as file:
        pics : dict = json.load(file)
    
    for bvid, image_url in pics.items():
        asyncio.run(download_thumbnail(bvid, image_url))