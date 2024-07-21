#include 'ps.jsx'



function extendImages() {
    var fileRef = new File(currentFolder + "副榜图片\\副榜样式1.psd")
    app.open(fileRef);

    if (app.documents.length > 0) {
        var doc = app.activeDocument;
        var thumbPositions = [
            [25, 23],
            [25, 296],
            [25, 567],
            [25, 838]
        ];
        var changePositions = [
            [492, 45],
            [492, 318],
            [492, 587],
            [492, 860]
        ];
        var dataToday = readJSONFile(currentFolder + "数据.json");

        // 确保读取的 JSON 数据有效
        if (dataToday) {
            $.writeln("已读取数据");
            for (var i = contain; i < extend; i++) {
                $.writeln("开始处理",i);
                var songData = dataToday[i];
                var layers = doc.layers[i % 4].layers;

                layers.getByName("排名").textItem.contents = String(i + 1);
                layers.getByName("得分").textItem.contents = comma(songData.point) + ' pts';

                // 导入封面

                var filePath = currentFolder + "封面\\" + songData.pic;
                var size = [100, 100];
                var position = thumbPositions[i % 4];
                var relativeObject = layers.getByName("点赞");
                var insertionLocation = ElementPlacement.PLACEAFTER;
                var thumbnailLayer = importImage(filePath, "封面", layers, relativeObject, insertionLocation, size, position);

                // 导入变化数据
                if (songData.change == "new") {
                    layers.getByName("前日排名").textItem.contents = "";
                    layers.getByName("前日").visible = false;
                    layers.getByName("new").visible = true;

                    var filePath = currentFolder + "其他图片\\小部件\\up.png";
                    var positionFix = [0, -18];
                } else {
                    layers.getByName("前日").visible = true;
                    layers.getByName("new").visible = false;

                    if (songData.change == "up") {
                        var filePath = currentFolder + "其他图片\\小部件\\up.png";
                        var positionFix = [0, -18];
                    } else if (songData.change == "cont") {
                        var filePath = currentFolder + "其他图片\\小部件\\cont.png";
                        var positionFix = [-14, 0];
                    } else if (songData.change == "down") {
                        var filePath = currentFolder + "其他图片\\小部件\\down.png";
                        var positionFix = [0, -18];
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
                var size = [31.6, 31.6]
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

                titleLayer = layers.getByName("标题")
                titleLayer.textItem.contents = songData.title;
                $.writeln('完成第' + (i + 1) + "位");
                resizeText(titleLayer, 1200);
                if (i % 4 == 3) {
                    savePic(doc, currentFolder + '副榜图片\\' + (i - 19) / 4 + ".png");
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

extendImages();