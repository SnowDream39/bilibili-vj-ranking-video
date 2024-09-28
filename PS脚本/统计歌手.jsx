#include 'ps.jsx'



function singerStatistics() {
    var mode = judgeMode();
    if (mode == 'daily' || mode == 'weekly'){
        var fileRef = new File(currentFolder + "其他图片\\统计歌手.psd");
    } else {
        var fileRef = new File(currentFolder + "其他图片\\统计歌手.psd");
    }
    app.open(fileRef);

    if (app.documents.length > 0) {
        var doc = app.activeDocument;
        var thumbPositions = [
            [23, 8],   [682, 8],
            [23, 224], [682, 224],
            [23, 440], [682, 440],
            [23, 656], [682, 656],
            [23, 872], [682, 872]
        ];
        var stats = readJSONFile(currentFolder + "统计.json");

        // 确保读取的 JSON 数据有效
        if (stats) {
            $.writeln("已读取数据");
            var vocalStats = stats['top_vocals'];
            for (var i = 0; i < 10; i++) {
                $.writeln("开始处理",i);
                var vocalData = vocalStats[i];
                var layers = doc.layers[i].layers;

                layers.getByName("排名").textItem.contents = vocalData.rank;
                layers.getByName("上期排名").textItem.contents = vocalData.rank_before;
                layers.getByName("名称").textItem.contents = vocalData.name;
                layers.getByName("总分").textItem.contents = comma(vocalData.point);
                layers.getByName("首位").textItem.contents = vocalData.highest_song;

                setFormattedText(textLayer = layers.getByName("首位"), contents = vocalData.highest_song, size = 30, font = "SourceHanSansCN-Regular", width=180);
                // 导入封面

                var filePath = currentFolder + "头像\\" + vocalData.name + ".png";
                var size = [78.125, 78.125];
                var position = thumbPositions[i];
                var relativeObject = layers.getByName("排名背景");
                var insertionLocation = ElementPlacement.PLACEBEFORE;
                var thumbnailLayer = importImage(filePath, "封面", layers, relativeObject, insertionLocation, size, position);
                thumbnailLayer.grouped = true;

                // 导入变化数据

                var changeLayers = layers.getByName("变化").layers;
                changeLayers.getByName("变化平").visible = false;
                changeLayers.getByName("变化升").visible = false;
                changeLayers.getByName("变化降").visible = false;
                if(vocalData.change === 'up'){
                    changeLayers.getByName("变化升").visible = true;
                }else if(vocalData.change === 'cont'){
                    changeLayers.getByName("变化平").visible = true;
                }else if(vocalData.change === 'down'){
                    changeLayers.getByName("变化降").visible = true;
                }


            }
        } else {
            $.writeln("读取 JSON 数据时出错");
        }
        savePic(doc, currentFolder + '其他图片\\统计歌手.png');
        doc.close(SaveOptions.SAVECHANGES);
    } else {
        $.writeln("没有活动文档");
    }
}

singerStatistics();