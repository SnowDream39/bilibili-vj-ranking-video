#include 'ps.jsx'


function newImages() {
    var fileRef = new File(currentFolder + "特刊图片\\梦的结唱样式3.psd");
    if (fileRef.exists) {
        app.open(fileRef);
    } else {
        $.writeln("文件不存在: " + fileRef);
    }

    // 确保有活动文档
    if (app.documents.length > 0) {
        var doc = app.activeDocument;
        var layers = doc.layers;
        var data = readJSONFile(currentFolder + "数据.json");
        var metadata = readJSONFile(currentFolder + "基本信息数据.json");
        // 先隐藏单项排名，保存好了之后再显示

        var items = ["播放", "收藏", "硬币", "点赞"];
        for (var i = 0; i < 4; i++) {
            var item = items[i];
            $.writeln(item);
            var itemLayers = layers.getByName(item).layers;
            itemLayers.getByName("位次").visible = false;
            itemLayers.getByName("位").visible = false;
        }
        // 确保读取的 JSON 数据有效
        if (data) {
            layers.getByName("上期排名").layers.getByName("标题").textItem.contents = metadata.title;
            for (var i = 0; i < data.length; i++) {
                var songData = data[i];

                layers.getByName("排名").textItem.contents = String.fromCharCode(songData.rank + 96);
                layers.getByName("得分").textItem.contents = comma(songData.point);
                layers.getByName("总补正").textItem.contents = '×' + songData.fix.toFixed(2) + ' =';

                fillSongInfo(layers.getByName("歌曲信息").layers, songData)

                fillData(songData, layers.getByName("播放").layers, ["view", "viewR", "view_rank"]);
                fillData(songData, layers.getByName("收藏").layers, ["favorite", "favoriteR", "favorite_rank"]);
                fillData(songData, layers.getByName("硬币").layers, ["coin", "coinR", "coin_rank"]);
                fillData(songData, layers.getByName("点赞").layers, ["like", "likeR", "like_rank"]);

                $.writeln('完成第' + (i+1) + "张图片");


                savePic(doc, currentFolder + 'PICKUP图片\\' + (songData.rank) + ".png");

                
            }

            // doc.close(SaveOptions.SAVECHANGES);
        } else {
            $.writeln("读取 JSON 数据时出错");
        }
        for (var i = 0; i < 4; i++) {
            var item = items[i];
            var itemLayers = layers.getByName(item).layers;
            itemLayers.getByName("位次").visible = true;
            itemLayers.getByName("位").visible = true;
        }
    } else {
        $.writeln("没有活动文档");
    }
}

newImages();