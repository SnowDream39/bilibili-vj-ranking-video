#include 'ps.jsx'

function newImages() {
    var mode = judgeMode();
    var fileRef = new File(currentFolder + "月回顾图片\\月回顾样式.psd");
    if (fileRef.exists) {
        app.open(fileRef);
    } else {
        $.writeln("文件不存在: " + fileRef);
    }
    part = 'review';

    // 确保有活动文档
    if (app.documents.length > 0) {
        var doc = app.activeDocument;
        var layers = doc.layers;
        var dataTodayNew = readJSONFile(currentFolder + "月回顾数据.json");

        // 确保读取的 JSON 数据有效
        if (dataTodayNew) {
            for (var i = 0; i < dataTodayNew.length; i++) {
                var songData = dataTodayNew[i];

                layers.getByName("排名").textItem.contents = songData.day;
                layers.getByName("得分").textItem.contents = comma(songData.point);

                fillSongInfo(layers.getByName("歌曲信息").layers, songData, mode, part);

                fillData(songData, layers.getByName("播放").layers, ["view", "viewR", "view_rank"]);
                fillData(songData, layers.getByName("收藏").layers, ["favorite", "favoriteR", "favorite_rank"]);
                fillData(songData, layers.getByName("硬币").layers, ["coin", "coinR", "coin_rank"]);
                fillData(songData, layers.getByName("点赞").layers, ["like", "likeR", "like_rank"]);

                $.writeln('完成月回顾第' + (i+1) + "张图片");
                savePic(doc, currentFolder + '月回顾图片\\' + (i+1) + ".png");
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