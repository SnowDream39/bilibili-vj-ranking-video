#include 'ps.jsx'

function fillSongInfo(layers, songData, mode, part) {
    
    setFormattedText(textLayer = layers.getByName("标题"), contents = songData.title, size = 54, font = "SourceHanSansCN-Bold", width=1430);
    setFormattedText(textLayer = layers.getByName("作者"), contents = songData.author, size = 48, font = "SourceHanSansCN-Bold", width=750);
    setFormattedText(textLayer = layers.getByName("歌手"), contents = songData.vocal, size = 36, font = "SourceHanSansCN-Bold", width=750);
    setFormattedText(textLayer = layers.getByName("引擎"), contents = songData.synthesizer, size = 36, font = "SourceHanSansCN-Bold", width=750);

    layers.getByName("BV号").textItem.contents = 'av' + songData.aid;
    layers.getByName("投稿时间").textItem.contents = songData.pubdate.substring(0, 16);
    layers.getByName("类型").textItem.contents = songData.type;
    if (songData.page == 1){
        layers.getByName("时长").textItem.contents = songData.duration; 
    }else{
        layers.getByName("时长").textItem.contents = songData.duration + "/" + songData.page + "P";
    }

    if (songData.copyright === 1 || songData.copyright === 4){
        var contents = "作者投稿";
    } else {
        var contents = "搬运：" + songData.uploader;
    }
    setFormattedText(textLayer = layers.getByName("copyright"), contents = contents, size = 36, font = "SourceHanSansCN-Bold", width=600);
    if (mode != 'monthly' && part == 'main') {
        layers.getByName("入榜次数").visible = true;
        layers.getByName("入榜次数").textItem.contents = "入榜次数：" + songData.count;
    } else {
        layers.getByName("入榜次数").visible = false;
    }
} 

function newImages() {
    var fileRef = new File(currentFolder + "特刊图片\\月冠样式.psd");
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
        // 确保读取的 JSON 数据有效
        if (data) {
            layers.getByName("上期排名").layers.getByName("标题").textItem.contents = metadata.title;
            for (var i = 0; i < 88; i++) {
                var songData = data[i];
                layers.getByName("上期排名").layers.getByName("标题").textItem.contents = songData.month;

                layers.getByName("排名").textItem.contents = i+1;
                layers.getByName("得分").textItem.contents = comma(songData.point);
                layers.getByName("总补正").textItem.contents = '×' + songData.fix.toFixed(2) + ' =';

                fillSongInfo(layers.getByName("歌曲信息").layers, songData)

                fillData(songData, layers.getByName("播放").layers, ["view", "viewR", "view_rank"]);
                fillData(songData, layers.getByName("收藏").layers, ["favorite", "favoriteR", "favorite_rank"]);
                fillData(songData, layers.getByName("硬币").layers, ["coin", "coinR", "coin_rank"]);
                fillData(songData, layers.getByName("点赞").layers, ["like", "likeR", "like_rank"]);

                $.writeln('完成第' + (i+1) + "张图片");
                savePic(doc, currentFolder + '特刊图片\\' + (i+1) + ".png");
            }

            // doc.close(SaveOptions.SAVECHANGES);
        } else {
            $.writeln("读取 JSON 数据时出错");
        }
    } else {
        $.writeln("没有活动文档");
    }
}

newImages();