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

function newImages() {
    var fileRef = new File(currentFolder + "新曲榜图片\\新曲榜样式1.psd");
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

        // 确保读取的 JSON 数据有效
        if (dataTodayNew) {
            for (var i = 0; i < dataTodayNew.length && i < 10; i++) {
                var songData = dataTodayNew[i];

                layers.getByName("新曲排名").textItem.contents = songData.rank;
                layers.getByName("得分").textItem.contents = comma(songData.point);

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

                $.writeln('完成新曲榜第' + (i+1) + "张图片");
                resizeText(titleLayer, 1380);
                savePic(doc, currentFolder + '新曲榜图片\\' + (i+1) + ".png");

            }

            doc.close(SaveOptions.SAVECHANGES);
        } else {
            $.writeln("读取 JSON 数据时出错");
        }
    } else {
        $.writeln("没有活动文档");
    }
}

newImages();