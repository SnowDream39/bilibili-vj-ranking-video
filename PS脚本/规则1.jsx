#include "ps.jsx"

function rule1() {
    var fileRef = new File(currentFolder + "其他图片\\规则1.psd");
    app.open(fileRef)
    // 确保有活动文档
    if (app.documents.length > 0) {
        var doc = app.activeDocument;
        var layers = doc.layers;
        var metadata = readJSONFile(currentFolder + "基本信息数据.json");

        // 确保读取的 JSON 数据有效
        if (metadata) {
            setFormattedText(textLayer = layers.getByName("标题"), contents = metadata.OP_title, size = 48, font = "SourceHanSansSC-Bold", width=1000);
            setFormattedText(textLayer = layers.getByName("作者"), contents = metadata.OP_author, size = 48, font = "SourceHanSansSC-Regular", width=1000);

            var position = [217, 206];
            var size = [117, 117];
            var relativeObject = layers.getByName("作者");
            var insertionLocation = ElementPlacement.PLACEBEFORE;
            var thumbLayer = importImage(currentFolder + '封面\\' + metadata.OP_bvid + '.png', "封面", layers, relativeObject, insertionLocation, size, position);
            savePic(doc, currentFolder + '其他图片\\规则1.png');
            doc.close(SaveOptions.SAVECHANGES);
        } else {
            $.writeln("读取 JSON 数据时出错");
        }
    } else {
        $.writeln("没有活动文档");
    }
}

rule1();