#include 'ps.jsx'


function quickImages() {
    var fileRef = new File(currentFolder + "省流版图片\\竖屏版样式2.psd");
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
                [55, 1265],
                [55, 1422],
                [55, 1579],
                [55, 1735]
            ];

            for (var i = 0; i < dataTodayNew.length*4 && i < 40; i++) {
                var songData = dataToday[i];
                var layers = doc.layers[i % 4].layers;

                layers.getByName("排名").textItem.contents = songData.rank;
                layers.getByName("得分").textItem.contents = comma(songData.point);

                // 导入封面

                var filePath = currentFolder + "封面\\" + songData.pic;
                var size = [58, 58];
                var position = thumbPositions[i % 4];
                var relativeObject = layers.getByName("点赞");
                var insertionLocation = ElementPlacement.PLACEAFTER;
                importImage(filePath, "封面", layers, relativeObject, insertionLocation, size, position);

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

                // layers.getByName("作者").textItem.contents = songData.author;
                layers.getByName("BV号").textItem.contents = songData.bvid;
                layers.getByName("投稿时间").textItem.contents = songData.pubdate.substring(0, 16);
                setFormattedText(textLayer = layers.getByName("标题"), contents = songData.title, size=25.16, font = "SourceHanSansSC-Bold", width = 650);
                $.writeln('完成第' + (i + 1) + "位");

                

                if (i % 4 == 3) {
                    var songData = dataTodayNew[(i - 3) / 4];
                    var layers = doc.layers;

                    layers.getByName("排名").textItem.contents = songData.rank;
                    layers.getByName("得分").textItem.contents = comma(songData.point);

                    fillData(songData, layers.getByName("播放").layers, ["view", "viewR", "view_rank"]);
                    fillData(songData, layers.getByName("收藏").layers, ["favorite", "favoriteR", "favorite_rank"]);
                    fillData(songData, layers.getByName("硬币").layers, ["coin", "coinR", "coin_rank"]);
                    fillData(songData, layers.getByName("点赞").layers, ["like", "likeR", "like_rank"]);

                    setFormattedText(textLayer = layers.getByName("标题"), contents = songData.title, size = 40, font = "SourceHanSansSC-Bold", width=1000);
                    setFormattedText(textLayer = layers.getByName("作者"), contents = songData.author, size = 36, font = "SourceHanSansSC-Bold", width=400);
                    setFormattedText(textLayer = layers.getByName("歌手"), contents = songData.vocal, size = 24, font = "SourceHanSansCN-Bold", width=400);
                    setFormattedText(textLayer = layers.getByName("引擎"), contents = songData.synthesizer, size = 24, font = "SourceHanSansCN-Bold", width=400);

                    layers.getByName("BV号").textItem.contents = songData.bvid;
                    layers.getByName("投稿时间").textItem.contents = songData.pubdate.substring(0, 16);
                    layers.getByName("时长").textItem.contents = songData.duration;
                    if (songData.copyright === 1){
                        var contents = "本家投稿";
                    } else {
                        var contents = "搬运：" + songData.uploader;
                    }
                    setFormattedText(textLayer = layers.getByName("copyright"), contents = contents, size = 22, font = "SourceHanSansCN-Regular", width=220);
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