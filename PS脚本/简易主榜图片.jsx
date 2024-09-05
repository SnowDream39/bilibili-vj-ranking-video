#include 'ps.jsx'



function easyMainImages() {
    var fileRef = new File(currentFolder + "副榜图片\\副榜样式2.psd")
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
            for (var i = 0; i < contain; i++) {
                $.writeln("开始处理",i);
                var songData = dataToday[i];
                var layers = doc.layers[i % 4].layers;

                layers.getByName("排名").textItem.contents = songData.rank;
                layers.getByName("得分").textItem.contents = comma(songData.point);

                // 导入封面

                var filePath = currentFolder + "封面\\" + songData.pic;
                var size = [100, 100];
                var position = thumbPositions[i % 4];
                var relativeObject = layers.getByName("点赞");
                var insertionLocation = ElementPlacement.PLACEAFTER;
                var thumbnailLayer = importImage(filePath, "封面", layers, relativeObject, insertionLocation, size, position);

                // 导入变化数据

                var changeLayers = layers.getByName("变化").layers;
                changeLayers.getByName("变化平").visible = false;
                changeLayers.getByName("变化升").visible = false;
                changeLayers.getByName("变化降").visible = false;
                if (songData.change == "new") {
                    layers.getByName("前日排名").textItem.contents = "";
                    layers.getByName("前日").visible = false;
                    layers.getByName("new").visible = true;
                    changeLayers.getByName("变化升").visible = true;
                } else {
                    layers.getByName("前日").visible = true;
                    layers.getByName("new").visible = false;
                    if (songData.change == "up") {
                        changeLayers.getByName("变化升").visible = true;
                    } else if (songData.change == "cont") {
                        changeLayers.getByName("变化平").visible = true;
                    } else if (songData.change == "down") {
                        changeLayers.getByName("变化降").visible = true;
                    }

                    if (songData.point_before == 0) {
                        layers.getByName("前日排名").textItem.contents = "--";
                    } else {
                        layers.getByName("前日排名").textItem.contents = songData.rank_before;
                    }
                }

                // var dataItems = ['播放', '收藏', '硬币', '点赞'];

                fillDataExtend(songData, layers.getByName("播放").layers, ["view", "view_rank"]);
                fillDataExtend(songData, layers.getByName("收藏").layers, ["favorite", "favorite_rank"]);
                fillDataExtend(songData, layers.getByName("硬币").layers, ["coin", "coin_rank"]);
                fillDataExtend(songData, layers.getByName("点赞").layers, ["like", "like_rank"]);

                layers.getByName("作者").textItem.contents = songData.author;
                layers.getByName("上榜次数").textItem.contents = "上榜次数：" + songData.count;
                layers.getByName("BV号").textItem.contents = songData.bvid;
                layers.getByName("BV号").textItem.contents = songData.bvid;
                layers.getByName("投稿时间").textItem.contents = songData.pubdate.substring(0, 16);

                setFormattedText(textLayer = layers.getByName("标题"), contents = songData.title, size=42.82, font = "SourceHanSansCN-Bold", width = 1100);
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