#include 'ps.jsx'


function quickImages() {
    var fileRef = new File(currentFolder + "省流版图片\\竖屏版样式1.psd");
    if (fileRef.exists) {
        app.open(fileRef);
    } else {
        $.writeln("文件不存在: " + fileRef);
    }

    // 确保有活动文档
    if (app.documents.length > 0) {
        var doc = app.activeDocument;
        var layers = doc.layers;
        var dataTodayNew = readJSONFile(currentFolder + "新曲数据.json");
        var dataToday = readJSONFile(currentFolder + '数据.json');

        // 确保读取的 JSON 数据有效
        if (dataTodayNew && dataToday) {
            var thumbPositions = [
                [60, 1196],
                [60, 1390],
                [60, 1585],
                [60, 1780]
            ];
            var changePositions = [
                [303, 1196],
                [303, 1390],
                [303, 1585],
                [303, 1780]
            ];

            for (var i = 0; i < dataTodayNew.length*4 && i < 40; i++) {
                var songData = dataToday[i];
                var layers = doc.layers[i % 4].layers;

                layers.getByName("排名").textItem.contents = songData.rank;
                layers.getByName("得分").textItem.contents = comma(songData.point) + ' pts';

                // 导入封面

                var filePath = currentFolder + "封面\\" + songData.pic;
                var size = [56, 56];
                var position = thumbPositions[i % 4];
                var relativeObject = layers.getByName("点赞");
                var insertionLocation = ElementPlacement.PLACEAFTER;
                importImage(filePath, "封面", layers, relativeObject, insertionLocation, size, position);

                // 导入变化数据
                if (songData.change == "new") {
                    layers.getByName("前日排名").textItem.contents = "";
                    layers.getByName("前日").visible = false;
                    layers.getByName("new").visible = true;

                    var filePath = currentFolder + "其他图片\\小部件\\up.png";
                    var positionFix = [0, 0];
                } else {
                    layers.getByName("前日").visible = true;
                    layers.getByName("new").visible = false;

                    if (songData.change == "up") {
                        var filePath = currentFolder + "其他图片\\小部件\\up.png";
                        var positionFix = [0, 0];
                    } else if (songData.change == "cont") {
                        var filePath = currentFolder + "其他图片\\小部件\\cont.png";
                        var positionFix = [-10, 13];
                    } else if (songData.change == "down") {
                        var filePath = currentFolder + "其他图片\\小部件\\down.png";
                        var positionFix = [0, 0];
                    }

                    if (songData.point_before == 0) {
                        layers.getByName("前日排名").textItem.contents = "--";
                    } else {
                        layers.getByName("前日排名").textItem.contents = songData.rank_before;
                    }
                }

                // 导入变化指示

                var position = changePositions[i % 4];
                var relativeObject = layers.getByName("new");
                var insertionLocation = ElementPlacement.PLACEBEFORE;
                var name = "变化";
                var size = [17.7, 17.7]
                var x = position[0] + positionFix[0];
                var y = position[1] + positionFix[1];
                var position = [x, y];
                
                importImage(filePath, "变化", layers, relativeObject, insertionLocation, size, position);


                // var dataItems = ['播放', '收藏', '硬币', '点赞'];

                fillDataExtend(songData, layers.getByName("播放").layers, ["view", "view_rank"]);
                fillDataExtend(songData, layers.getByName("收藏").layers, ["favorite", "favorite_rank"]);
                fillDataExtend(songData, layers.getByName("硬币").layers, ["coin", "coin_rank"]);
                fillDataExtend(songData, layers.getByName("点赞").layers, ["like", "like_rank"]);

                // layers.getByName("作者").textItem.contents = songData.author;
                layers.getByName("BV号").textItem.contents = songData.bvid;
                layers.getByName("投稿时间").textItem.contents = songData.pubdate.substring(0, 16);
                setFormattedText(textLayer = layers.getByName("标题"), contents = songData.title, size=36, font = "SourceHanSansCN-Regular", width = 950);
                $.writeln('完成第' + (i + 1) + "位");

                

                if (i % 4 == 3) {
                    var songData = dataTodayNew[(i - 3) / 4];
                    var layers = doc.layers;

                    layers.getByName("排名").textItem.contents = songData.rank;
                    layers.getByName("得分").textItem.contents = comma(songData.point) + ' pts';

                    fillData(songData, layers.getByName("播放").layers, ["view", "viewR", "view_rank"]);
                    fillData(songData, layers.getByName("收藏").layers, ["favorite", "favoriteR", "favorite_rank"]);
                    fillData(songData, layers.getByName("硬币").layers, ["coin", "coinR", "coin_rank"]);
                    fillData(songData, layers.getByName("点赞").layers, ["like", "likeR", "like_rank"]);

                    var otherInfoLayer = layers.getByName("其他信息");
                    var otherInfo = songData.author + " | 引擎：" + songData.synthesizer + " | 歌手：" + songData.vocal;
                    setFormattedText(textLayer = otherInfoLayer, contents = otherInfo, size = 30, font = "MicrosoftYaHei-Bold", width=950);
                    layers.getByName("BV号").textItem.contents = songData.bvid;
                    layers.getByName("投稿时间").textItem.contents = songData.pubdate.substring(0, 16);
                    setFormattedText(textLayer = layers.getByName("标题"), contents = songData.title, size=36, font = "SourceHanSansCN-Regular", width = 950);
                    $.writeln('完成新曲榜第' + (i + 1) + "张图片");
                    savePic(doc, currentFolder + '省流版图片\\' + ((i + 1) / 4) + ".png");
                }

            }

            var doc = app.activeDocument;

            // 确保读取的 JSON 数据有效
            if (dataToday) {
                $.writeln("已读取数据");


            }
        } else {
            $.writeln("读取 JSON 数据时出错");
        }
        doc.close(SaveOptions.SAVECHANGES);
    } else {
        $.writeln("没有活动文档");
    }
}

quickImages();