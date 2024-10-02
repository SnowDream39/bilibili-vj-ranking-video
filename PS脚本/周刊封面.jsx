#include 'ps.jsx'


function thumbnail() {
    var mode = judgeMode();

    var inputFiles = [ new File(currentFolder + "其他图片\\周刊\\4比3封面.psd"),  new File(currentFolder + "其他图片\\周刊\\16比9封面.psd") ];
    var thumbnails = currentFolder + '其他图片\\最高新曲封面4比3.png';
    var outputFiles = [currentFolder + '其他图片\\4比3封面.png', currentFolder + '其他图片\\16比9封面.png']
    var positions = [[1030,366], [1030, 186]];


    for(var i=0; i<inputFiles.length; i++){

        app.open(inputFiles[i]);
        // 确保有活动文档
        if (app.documents.length > 0) {
            var doc = app.activeDocument;
            var layers = doc.layers;
            var metadata = readJSONFile(currentFolder + "基本信息数据.json");

            // 确保读取的 JSON 数据有效
            if (metadata) {
                var weekday = metadata.weekday;

                layers.getByName("日期").textItem.contents = metadata.full_date;
                layers.getByName("总期数").textItem.contents = "#" + metadata.total_phase;

            } else {
                $.writeln("读取 JSON 数据时出错");
            }
            var position = positions[i];
            var size = [43.5, 43.5];
            var relativeObject = layers.getByName("封面框");
            var insertionLocation = ElementPlacement.PLACEBEFORE;
            var thumbLayer = importImage(thumbnails, "封面", layers, relativeObject, insertionLocation, size, position);
            thumbLayer.grouped = true;
            savePic(doc, outputFiles[i]);
            doc.close(SaveOptions.SAVECHANGES);
        } else {
            $.writeln("没有活动文档");
        }

    }
}

thumbnail();