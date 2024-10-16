#include 'ps.jsx'

function thumbnail16to9() {
    var fileRef = new File(currentFolder + "其他图片\\专栏封面.psd")
    app.open(fileRef);
    // 确保有活动文档
    if (app.documents.length > 0) {
        var doc = app.activeDocument;
        var layers = doc.layers;
        var metadata = readJSONFile(currentFolder + "基本信息数据.json");

        // 确保读取的 JSON 数据有效
        if (metadata) {

            layers.getByName("年").textItem.contents = metadata.year;
            layers.getByName("月").textItem.contents = padNumber(metadata.month, 2) + '/';
            layers.getByName("日").textItem.contents = padNumber(metadata.day, 2);
            layers.getByName("总期数").textItem.contents = "总第"+ padNumber(metadata.total_phase, 5) + "期";
            layers.getByName("期数").textItem.contents = padNumber(metadata.phase, 3);
            $.writeln(metadata.date);
        } else {
            $.writeln("读取 JSON 数据时出错");
        }
        var position = [0, -104];
        var size = [54, 54];
        var relativeObject = layers.getByName("背景");
        var insertionLocation = ElementPlacement.PLACEBEFORE;
        var thumbLayer = importImage(currentFolder + '其他图片\\最高新曲封面16比9.png', "封面", layers, relativeObject, insertionLocation, size, position);
        savePic(doc, currentFolder + '其他图片\\专栏封面.png');
        doc.close(SaveOptions.SAVECHANGES);
    } else {
        $.writeln("没有活动文档");
    }
}

thumbnail16to9();