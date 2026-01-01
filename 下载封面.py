import json
import asyncio
import random
import time
from bilibili_api import video, HEADERS
import requests
from PIL import Image
from io import BytesIO
import os
from urllib.parse import urlparse

# 模拟浏览器User-Agent列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
]

def get_random_headers():
    """获取随机请求头，模拟真实浏览器"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.bilibili.com/',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'image',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'cross-site',
    }

def download_with_retry(url, headers, max_retries=3, timeout=30):
    """带重试机制的下载函数"""
    for attempt in range(max_retries):
        try:
            # 添加随机延迟，避免请求过于频繁
            if attempt > 0:
                delay = random.uniform(1, 3) * (attempt + 1)
                print(f"等待 {delay:.2f} 秒后重试...")
                time.sleep(delay)
            
            response = requests.get(
                url, 
                headers=headers, 
                timeout=timeout,
                stream=True  # 流式下载，适合大文件
            )
            response.raise_for_status()  # 检查HTTP错误
            
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"下载失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise
            # 更换User-Agent重试
            headers['User-Agent'] = random.choice(USER_AGENTS)
    
    return None

async def get_thumbnail(bvid) -> str:
    """获取视频缩略图URL"""
    v = video.Video(bvid=bvid)
    response = await v.get_info()
    return response["pic"]

async def download_thumbnail(bvid, image_url):
    """下载并处理普通封面"""
    print(f"正在下载封面：{bvid}")
    
    try:
        headers = get_random_headers()
        response = download_with_retry(image_url, headers)
        
        if response and response.status_code == 200:
            # 流式读取图片内容
            image_content = response.content
            image = Image.open(BytesIO(image_content))
            
            # 验证图片有效性
            image.verify()  # 验证图片完整性
            image = Image.open(BytesIO(image_content))  # 需要重新打开，因为verify会关闭文件
            
            print(f"成功下载 {bvid} 的封面，尺寸: {image.width}x{image.height}")
        else:
            print(f"图片下载失败，状态码：{response.status_code if response else 'None'}")
            return False
            
    except Exception as e:
        print(f"下载封面 {bvid} 时出错：{e}")
        return False

    try:
        # 16:9 裁剪
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

        cropped_image = image.crop((int(left), int(top), int(right), int(bottom)))
        resized_image = cropped_image.resize((352, 199), Image.Resampling.LANCZOS)

        output_path = "封面/" + bvid + ".png"
        resized_image.save(output_path, "PNG", optimize=True)
        print(f"已保存封面到: {output_path}")
        return True
        
    except Exception as e:
        print(f"处理封面 {bvid} 时出错：{e}")
        return False

async def download_thumbnail_special(image_url):
    """下载特殊比例封面（4:3 和 16:9）"""
    print("正在下载特殊封面...")
    
    try:
        headers = get_random_headers()
        response = download_with_retry(image_url, headers)
        
        if response and response.status_code == 200:
            image_content = response.content
            image = Image.open(BytesIO(image_content))
            
            # 验证图片有效性
            image.verify()
            image = Image.open(BytesIO(image_content))
            
            print(f"成功下载特殊封面，原始尺寸: {image.width}x{image.height}")
        else:
            print(f"特殊封面下载失败，状态码：{response.status_code if response else 'None'}")
            return False
            
    except Exception as e:
        print(f"下载特殊封面时出错：{e}")
        return False

    try:
        # 4比3裁剪
        if image.width / image.height > 4 / 3:
            left = image.width / 2 - image.height / 3 * 2
            right = image.width / 2 + image.height / 3 * 2
            top = 0
            bottom = image.height
        else:
            top = image.height / 2 - image.width / 8 * 3
            bottom = image.height / 2 + image.width / 8 * 3
            left = 0
            right = image.width

        cropped_image = image.crop((int(left), int(top), int(right), int(bottom)))
        resized_image = cropped_image.resize((1920, 1440), Image.Resampling.LANCZOS)
        output_path_4_3 = "其他图片/最高新曲封面4比3.png"
        resized_image.save(output_path_4_3, "PNG", optimize=True)
        print(f"已保存4:3特殊封面到: {output_path_4_3}")

        # 16比9裁剪
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

        cropped_image = image.crop((int(left), int(top), int(right), int(bottom)))
        resized_image = cropped_image.resize((1920, 1080), Image.Resampling.LANCZOS)
        output_path_16_9 = "其他图片/最高新曲封面16比9.png"
        resized_image.save(output_path_16_9, "PNG", optimize=True)
        print(f"已保存16:9特殊封面到: {output_path_16_9}")
        
        return True
        
    except Exception as e:
        print(f"处理特殊封面时出错：{e}")
        return False

async def download_thumbnails_from_list(bvids_with_urls):
    """从BV号和URL列表下载封面（限制并发数，避免过于频繁的请求）"""
    if not os.path.exists("封面"):
        os.makedirs("封面")
    
    if not os.path.exists("其他图片"):
        os.makedirs("其他图片")
    
    # 限制并发数量，避免同时发起太多请求
    semaphore = asyncio.Semaphore(5)  # 最多同时5个下载任务
    failed_downloads = []
    
    async def download_with_semaphore(bvid, image_url):
        async with semaphore:
            # 添加随机延迟，避免请求过于集中
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
            if len(image_url) == 0:
                # 如果没有提供URL，需要从B站API获取
                try:
                    image_url = await get_thumbnail(bvid)
                except Exception as e:
                    print(f"获取 {bvid} 的封面URL失败：{e}")
                    return bvid, False
            
            success = await download_thumbnail(bvid, image_url)
            return bvid, success
    
    # 创建下载任务
    tasks = []
    for bvid, image_url in bvids_with_urls.items():
        tasks.append(download_with_semaphore(bvid, image_url))
    
    if tasks:
        # 分批执行，避免一次性处理太多
        batch_size = 10
        for i in range(0, len(tasks), batch_size):
            batch_tasks = tasks[i:i + batch_size]
            results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # 统计失败的下载
            for result in results:
                if isinstance(result, Exception):
                    print(f"下载过程中出现异常：{result}")
                elif isinstance(result, tuple):
                    bvid, success = result
                    if not success:
                        failed_downloads.append(bvid)
            
            # 批次间添加延迟
            if i + batch_size < len(tasks):
                print(f"已完成 {min(i + batch_size, len(tasks))}/{len(tasks)} 个封面下载，等待 2 秒后继续...")
                await asyncio.sleep(2)
        
        # 输出失败的下载
        if failed_downloads:
            print(f"\n以下封面下载失败：")
            for bvid in failed_downloads:
                print(f"  - {bvid}")
            
            # 保存失败的下载列表
            with open("下载失败的封面.json", "w", encoding="utf-8") as file:
                json.dump(failed_downloads, file, ensure_ascii=False, indent=4)
            print("已将失败的下载列表保存到 下载失败的封面.json")

async def download_special_thumbnail(image_url):
    """下载特殊封面"""
    if not os.path.exists("其他图片"):
        os.makedirs("其他图片")
    
    await download_thumbnail_special(image_url)

async def main():
    """主函数，读取BV号列表并下载封面"""
    try:
        print("=" * 50)
        print("封面下载脚本启动")
        print("=" * 50)
        
        total_success = True
        
        # 读取普通封面下载列表
        if os.path.exists("新增封面.json"):
            with open("新增封面.json", "r", encoding="utf-8") as file:
                today_pics = json.load(file)
                if today_pics:
                    print(f"开始下载 {len(today_pics)} 个普通封面...")
                    start_time = time.time()
                    await download_thumbnails_from_list(today_pics)
                    end_time = time.time()
                    print(f"普通封面下载完成，耗时: {end_time - start_time:.2f} 秒")
                else:
                    print("没有需要下载的普通封面")
        else:
            print("未找到 新增封面.json 文件")
        
        # 检查是否有特殊封面需要下载
        if os.path.exists("特殊封面.json"):
            with open("特殊封面.json", "r", encoding="utf-8") as file:
                special_data = json.load(file)
                if 'special_thumbnail_url' in special_data:
                    try:
                        print("开始下载特殊封面...")
                        start_time = time.time()
                        await download_special_thumbnail(special_data['special_thumbnail_url'])
                        end_time = time.time()
                        print(f"特殊封面下载完成，耗时: {end_time - start_time:.2f} 秒")
                    except Exception as e:
                        total_success = False
                        print(f"下载特殊封面时出错：{e}")
                else:
                    print("特殊封面数据格式错误")
        else:
            print("未找到 特殊封面.json 文件")
        
        print("=" * 50)
        if total_success:
            print("所有封面下载任务完成！")
        else:
            print("部分封面下载失败，请检查 下载失败的封面.json")
        print("=" * 50)
        
    except Exception as e:
        print(f"下载封面时出现严重错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())