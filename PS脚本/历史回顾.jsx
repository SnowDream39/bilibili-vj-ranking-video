#include 'ps.jsx'



function history() {
    var mode = judgeMode();
    var fileRef = new File(currentFolder + "其他图片\\历史回顾.psd");
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
        var stats = readJSONFile(currentFolder + "历史数据.json");

        // 确保读取的 JSON 数据有效
        if (stats) {
            $.writeln("已读取数据");
            for (var i=0; i<5; ++i) {
                $.writeln("开始处理",i);
                var songData = stats[i];
                var pos = i;
                doc.layers[pos].visible = true;
                var layers = doc.layers[pos].layers;

                setFormattedText(textLayer = layers.getByName("标题"), contents = songData.title, size = 32, font = "SourceHanSansCN-Bold", width=650);
                layers.getByName("作者").textItem.contents = songData.author;
                layers.getByName("总分").textItem.contents = comma(songData.point);
                layers.getByName("BV号").textItem.contents = songData.bvid;

                // 导入封面

                var filePath = currentFolder + "封面\\" + songData.bvid + ".png";
                var size = [75, 75];
                var position = thumbPositions[pos];
                var relativeObject = layers.getByName("百万背景");
                var insertionLocation = ElementPlacement.PLACEBEFORE;
                var thumbnailLayer = importImage(filePath, "封面", layers, relativeObject, insertionLocation, size, position);

            }

            savePic(doc, currentFolder + '其他图片\\历史回顾' + '.png')
        } else {
            $.writeln("读取 JSON 数据时出错");
        }
        doc.close(SaveOptions.SAVECHANGES);
    } else {
        $.writeln("没有活动文档");
    }
}

history();