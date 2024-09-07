# 术力口数据姬

这是bilibili平台上[术力口数据姬](https://space.bilibili.com/3546611315640327)的视频和图文制作脚本。

这个仓库内包含了日刊、周刊、月刊、省流版日刊、每日冠军回顾以及图文版的制作脚本。PS和PR工程文件因为较大，没有放在版本库中。

## 运行环境

- VSCode
- Python 3.7以上
- Adobe Premiere Pro
- Adobe Photoshop

## 视频制作方法

1. 将数据文件放入文件夹
2. 运行`准备资源.py`，使用对应的模式（日刊、图文版、周刊、月刊）
3. 打开PS，运行`PS脚本`文件夹中对应的图片脚本
4. 打开PR，打开`完整刊.prproj`，导入新视频到`截取片段视频`素材箱当中，进行打点，然后运行`提取截取片段.jsx`
5. 打开`PR脚本/完整刊.jsx`文件，手动修改开头的`MODE`（`daily`或`weekly`或`monthly`），然后运行

## 省流版制作方法

准备资源与上面相同
1. 打开PS，运行`PS脚本/省流版图片.jsx`（如果制作日刊时已经制作省流版图片则跳过）
2. 打开PR，打开`省流版日刊.prproj`
3. 运行`PR脚本/小日刊.jsx`

## 图文版制作方法

准备资源与上面相同
1. 运行`生成文章.py`
2. 生成的文章位于`专栏文本.html`，全文复制
3. 前往bilibili投稿专栏，使用旧版编辑器，利用[Markdown编辑工具](https://github.com/LuckyPuppy514/Bilibili-Markdown)，粘贴
4. 其他图片使用复制粘贴的方法加入文章

## 视频打点的具体方法

在PR当中，`I`键标记剪辑入点，`O`键标记剪辑出点。

日刊默认的截取长度是20秒。在打点的时候，只需要标记入点与出点两者中的一个。

只要没有标记入点（也就是说，入点位于视频的开头），脚本就会根据出点来计算入点，否则根据入点来计算出点。

## 使用注意

本项目使用MIT许可证进行许可。

不过要想制作日刊，还需要PS和PR工程文件（用作模板）以及数据文件，也就是说仅靠这个仓库你是做不出视频的。想要工程文件请联系SnowDream39。关于数据脚本，请前往[SnowDream39/bilibili_vj_ranking](https://github.com/SnowDream39/bilibili_vj_ranking)。

注意`ps.jsx`和`pr.jsx`两个文件当中的`currentFolder`变量需要在第一次使用前手动更改。