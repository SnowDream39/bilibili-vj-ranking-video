#include 'ps.jsx'



function easyMainImages() {
    var mode = judgeMode();
    var fileRef = new File(currentFolder + "副榜图片\\副榜样式.psd")
    app.open(fileRef);

    if (app.documents.length > 0) {
        var doc = app.activeDocument;
        var thumbPositions = [
            [125, 38],
            [125, 305],
            [125, 572],
            [125, 838]
        ];
        var dataToday = readJSONFile(currentFolder + "数据.json");

        // 确保读取的 JSON 数据有效
        if (dataToday) {
            $.writeln("已读取数据");
            for (var i = 0; i <40; i++) {
                $.writeln("开始处理",i);
                var songData = dataToday[i];
                var layers = doc.layers[i % 4].layers;

                layers.getByName("排名").textItem.contents = songData.rank;
                layers.getByName("得分").textItem.contents = comma(songData.point);

                // 导入封面

                var filePath = currentFolder + "封面\\" + songData.pic;
                var size = [100, 100];
                var position = thumbPositions[i % 4];
                var relativeObject = layers.getByName("歌手颜色");
                var insertionLocation = ElementPlacement.PLACEBEFORE;
                var thumbnailLayer = importImage(filePath, "封面", layers, relativeObject, insertionLocation, size, position);

                // 导入变化数据
                fillBeforeRankExtend(layers, songData, mode);

                // var dataItems = ['播放', '收藏', '硬币', '点赞'];

                fillDataExtend(songData, layers.getByName("播放").layers, ["view", "view_rank"]);
                fillDataExtend(songData, layers.getByName("收藏").layers, ["favorite", "favorite_rank"]);
                fillDataExtend(songData, layers.getByName("硬币").layers, ["coin", "coin_rank"]);
                fillDataExtend(songData, layers.getByName("点赞").layers, ["like", "like_rank"]);

                fillSongInfoExtend(layers, songData, mode);
                $.writeln('完成第' + (i + 1) + "位");
                if (i % 4 == 3) {
                    savePic(doc, currentFolder + '简易主榜图片\\' + (i+1) / 4 + ".png");
                }

            }
        } else {
            $.writeln("读取 JSON 数据时出错");
        }
        doc.close(SaveOptions.SAVECHANGES);
    } else {
        $.writeln("没有活动文档");
    }
}

easyMainImages();