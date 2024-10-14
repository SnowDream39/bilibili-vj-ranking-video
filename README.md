# 术力口数据姬

这是bilibili平台上[术力口数据姬](https://space.bilibili.com/3546611315640327)的视频和图文制作脚本。

这个仓库内包含了日刊、周刊、月刊、省流版日刊、每日冠军回顾以及图文版的制作脚本。PS和PR工程文件因为较大，在Release当中提供。

## 运行环境

- VSCode
- Python 3.7以上
- Adobe Premiere Pro 2024
- Adobe Photoshop 2024 

## 初始化配置方法（VSCode）

1. 下载项目代码，以及最新的Release文件，放在一起。
2. `ps.jsx`和`pr.jsx`两个文件当中的`currentFolder`变量需要在第一次使用前手动更改为当前项目目录。
3. 在VSCode扩展商店中下载`ExtendScript Debugger`

## 视频制作方法

1. 将数据文件放入文件夹
2. 打开`准备资源.py`，选择`使用 launch.json 进行调试`，使用对应的模式（日刊、图文版、周刊、月刊）
3. 打开PS，运行`PS脚本`文件夹中对应的图片脚本
4. 打开PR，打开`完整刊.prproj`，导入新视频到`截取片段视频`素材箱当中，进行打点，然后运行`提取截取片段.jsx`
5. 打开`PR脚本/完整刊.jsx`文件，手动修改开头的`MODE`（`daily`或`weekly`或`monthly`），然后运行


## 图文版制作方法

先执行到视频制作的第2步
1. 打开PS，运行`PS脚本`文件夹中对应的图片脚本
2. 运行`生成文章.py`
3. 生成的文章位于`专栏文本.html`，全文复制源代码
4. 前往bilibili投稿专栏，使用旧版编辑器，利用[Markdown编辑工具](https://github.com/LuckyPuppy514/Bilibili-Markdown)，粘贴
5. 其他图片使用复制粘贴的方法加入文章

## 视频打点的具体方法

在PR当中，`I`键标记剪辑入点，`O`键标记剪辑出点。

日刊默认的截取长度是20秒。在打点的时候，只需要标记入点与出点两者中的一个。

只要没有标记入点（也就是说，入点位于视频的开头），脚本就会根据出点来计算入点，否则根据入点来计算出点。

## 数据可视化工具

项目中包含了经修改过的[动态排名数据可视化工具](https://github.com/Jannchie/Historical-ranking-data-visualization-based-on-d3.js)。

修改主要是加入歌姬颜色和头像，还有适合 1920*1080 分辨率的屏幕方便录制视频。这些配置都可以进一步调整。

使用方法：
1.使用'`统计推移`中的脚本生成数据`csv`文件。
2.打开`可视化/src/bargraph.html`，然后选择生成的`csv`文件。

## 使用注意

本项目使用GPLv3许可证进行许可。

关于数据脚本，请前往[SnowDream39/bilibili_vj_ranking](https://github.com/SnowDream39/bilibili_vj_ranking)。

