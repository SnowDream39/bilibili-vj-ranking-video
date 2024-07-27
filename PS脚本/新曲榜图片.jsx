#include 'ps.jsx'


function newImages() {
    var fileRef = new File(currentFolder + "新曲榜图片\\新曲榜样式2.psd");
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

                setFormattedText(textLayer = layers.getByName("标题"), contents = songData.title, size = 60, font = "SourceHanSansSC-Bold", width=1330);
                setFormattedText(textLayer = layers.getByName("作者"), contents = songData.author, size = 48, font = "SourceHanSansSC-Bold", width=650);
                setFormattedText(textLayer = layers.getByName("歌手"), contents = songData.vocal, size = 36, font = "SourceHanSansCN-Bold", width=650);
                setFormattedText(textLayer = layers.getByName("引擎"), contents = songData.synthesizer, size = 36, font = "SourceHanSansCN-Bold", width=650);

                layers.getByName("BV号").textItem.contents = songData.bvid;
                layers.getByName("投稿时间").textItem.contents = songData.pubdate.substring(0, 16);
                layers.getByName("时长").textItem.contents = songData.duration;
                if (songData.copyright === 1){
                    var contents = "本家投稿";
                } else {
                    var contents = "搬运：" + songData.uploader;
                }
                setFormattedText(textLayer = layers.getByName("copyright"), contents = contents, size = 36, font = "SourceHanSansCN-Bold", width=350);

                $.writeln('完成新曲榜第' + (i+1) + "张图片");
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