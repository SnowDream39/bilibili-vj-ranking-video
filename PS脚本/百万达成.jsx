#include 'ps.jsx'



function millionReach() {
    var mode = judgeMode();
    var fileRef = new File(currentFolder + "其他图片\\百万达成.psd");
    app.open(fileRef);

    if (app.documents.length > 0) {
        var doc = app.activeDocument;
        var thumbPositions = [
            [137, 31], 
            [137, 248],
            [137, 465],
            [137, 682],
            [137, 899]
        ];
        var stats = readJSONFile(currentFolder + "百万达成.json");

        // 确保读取的 JSON 数据有效
        if (stats) {
            $.writeln("已读取数据");
            var i=0;
            while (i<stats.length) {
                $.writeln("开始处理",i);
                var songData = stats[i];
                var pos = i%5;
                doc.layers[pos].visible = true;
                var layers = doc.layers[pos].layers;

                setFormattedText(textLayer = layers.getByName("标题"), contents = songData.title, size = 32, font = "SourceHanSansCN-Bold", width=750);
                layers.getByName("作者").textItem.contents = songData.author;
                layers.getByName("数值").textItem.contents = songData.million_crossed + "00万";
                layers.getByName("投稿日期").textItem.contents = songData.pubdate.substring(0,10);

                // 导入封面

                var filePath = currentFolder + "封面\\" + songData.bvid + ".png";
                var size = [75, 75];
                var position = thumbPositions[pos];
                var relativeObject = layers.getByName("百万背景");
                var insertionLocation = ElementPlacement.PLACEBEFORE;
                var thumbnailLayer = importImage(filePath, "封面", layers, relativeObject, insertionLocation, size, position);

                if (pos == 4) {
                    savePic(doc, currentFolder + '其他图片\\百万达成' + (i+1)/5 + '.png')
                }

                i = i + 1;
            }
            pos = pos + 1;
            while (pos < 5){
                doc.layers[pos].visible = false;
                pos = pos + 1;
                i = i + 1;
            }
            savePic(doc, currentFolder + '其他图片\\百万达成' + ((i-pos)/5 + 1) + '.png')
        } else {
            $.writeln("读取 JSON 数据时出错");
        }
        doc.close(SaveOptions.SAVECHANGES);
    } else {
        $.writeln("没有活动文档");
    }
}

millionReach();