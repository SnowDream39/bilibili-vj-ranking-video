#include 'ps.jsx'

function fillData(songData, layers, keys) {
    layers.getByName("数值").textItem.contents = comma(songData[keys[0]]);
    layers.getByName("修正").textItem.contents = '×' + songData[keys[1]].toFixed(2);
    layers.getByName("位次").textItem.contents = songData[keys[2]] + '位';
    if (songData[keys[2]] === Math.min(songData.view_rank, songData.favorite_rank, songData.coin_rank, songData.like_rank)) {
        setColor(layers.getByName("位次").textItem, 'red');
    } else {
        setColor(layers.getByName("位次").textItem, 'black');
    }
}

function mainImages() {
    var fileRef = new File(currentFolder + "主榜图片\\主榜样式1.psd");
    if (fileRef.exists) {
        app.open(fileRef);
    } else {
        $.writeln("文件不存在: " + filePath);
    }

    // 确保有活动文档
    if (app.documents.length > 0) {
        var doc = app.activeDocument;
        var layers = doc.layers;
        var dataToday = readJSONFile(currentFolder + "数据.json");

        // 确保读取的 JSON 数据有效
        if (dataToday) {
            for (var i = 0; i < contain; i++) {
                var songData = dataToday[i];

                layers.getByName("排名").textItem.contents = String(i + 1);
                layers.getByName("得分").textItem.contents = comma(songData.point);

                if (songData.change == "new") {
                    layers.getByName("前日排名").textItem.contents = "";
                    layers.getByName("前日得分").textItem.contents = "";
                    layers.getByName("new").visible = true;
                    for (var j = 0; j < layers.length; j++) {
                        if (layers[j].name == "变化") {
                            layers[j].remove();
                        }
                    }
                    var filePath = currentFolder + "其他图片\\小部件\\up.png";
                    var positionFix = [0, -16];
                } else {
                    layers.getByName("new").visible = false;
                    if (songData.change == "up") {
                        var filePath = currentFolder + "其他图片\\小部件\\up.png";
                        var positionFix = [0, -16];
                    } else if (songData.change == "cont") {
                        var filePath = currentFolder + "其他图片\\小部件\\cont.png";
                        var positionFix = [-13, 0];
                    } else if (songData.change == "down") {
                        var filePath = currentFolder + "其他图片\\小部件\\down.png";
                        var positionFix = [0, -13];
                    }

                    if (songData.point_before == 0) {
                        layers.getByName("前日排名").textItem.contents = "--";
                        layers.getByName("前日得分").textItem.contents = "--";
                    } else {
                        layers.getByName("前日排名").textItem.contents = songData.rank_before;
                        layers.getByName("前日得分").textItem.contents = comma(songData.point_before);
                    }

                }

                // 导入变化指示

                var position = [1516, 334];
                var size = [27, 27];
                var relativeObject = layers.getByName("new");
                var insertionLocation = ElementPlacement.PLACEAFTER;
                var name = "变化"
                var changeLayer = importImage(filePath, name, layers, relativeObject, insertionLocation, size, position);

                // var dataItems = ['播放', '收藏', '硬币', '点赞']; 

                fillData(songData, layers.getByName("播放").layers, ["view", "viewR", "view_rank"]);
                fillData(songData, layers.getByName("收藏").layers, ["favorite", "favoriteR", "favorite_rank"]);
                fillData(songData, layers.getByName("硬币").layers, ["coin", "coinR", "coin_rank"]);
                fillData(songData, layers.getByName("点赞").layers, ["like", "likeR", "like_rank"]);

                layers.getByName("作者").textItem.contents = songData.author;
                layers.getByName("BV号").textItem.contents = songData.bvid;
                layers.getByName("投稿时间").textItem.contents = songData.pubdate.substring(0, 16);
                layers.getByName("时长").textItem.contents = songData.duration;
                var copyrightLayer = layers.getByName("copyright");
                if (songData.copyright == 1){
                    copyrightLayer.textItem.contents = "本家投稿";
                } else {
                    copyrightLayer.textItem.contents = "搬运：" + songData.uploader;
                }
                resizeText(copyrightLayer, 250);
                titleLayer = layers.getByName("标题")
                titleLayer.textItem.contents = songData.title;


                $.writeln('完成第' + i + "张图片");
                resizeText(titleLayer, 1380);
                savePic(doc, currentFolder + '主榜图片\\' + (i + 1) + ".png");
            }

            doc.close(SaveOptions.SAVECHANGES);
        } else {
            $.writeln("读取 JSON 数据时出错");
        }
    } else {
        $.writeln("没有活动文档");
    }
}

mainImages();