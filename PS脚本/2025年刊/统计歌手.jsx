#include '../ps.jsx'



function singerStatistics() {
    var mode = judgeMode();
    var fileRef = new File(currentFolder + "特刊图片\\2025年刊\\统计歌手.psd");
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
        var stats = readJSONFile(currentFolder + "统计歌手.json");

        // 确保读取的 JSON 数据有效
        if (stats) {
            $.writeln("已读取数据");
            var vocalStats = stats;
            for (var i = 0; i < 30; i++) {
                $.writeln("开始处理",i);
                var vocalData = vocalStats[i];
                var layers = doc.layers[i%10].layers;

                layers.getByName("排名").textItem.contents = vocalData.rank;
                layers.getByName("名称").textItem.contents = vocalData.vocal;
                layers.getByName("总分").textItem.contents = comma(vocalData.point);

                // 导入封面

                var filePath = currentFolder + "头像\\" + vocalData.vocal + ".png";
                var size = [78.125, 78.125];
                var position = thumbPositions[i%10];
                var relativeObject = layers.getByName("排名背景");
                var insertionLocation = ElementPlacement.PLACEBEFORE;
                var thumbnailLayer = importImage(filePath, "封面", layers, relativeObject, insertionLocation, size, position);
                thumbnailLayer.grouped = true;


                if (i % 10 == 9){

                    savePic(doc, currentFolder + '特刊图片\\2025年刊\\统计歌手' + (i+1)/10 + '.png');
                }

            }
        } else {
            $.writeln("读取 JSON 数据时出错");
        }
        doc.close(SaveOptions.SAVECHANGES);
    } else {
        $.writeln("没有活动文档");
    }
}

singerStatistics();