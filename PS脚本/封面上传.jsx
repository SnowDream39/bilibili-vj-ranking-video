#include 'ps.jsx'

function thumbnailUpload() {
    var fileRef = new File(currentFolder + "其他图片\\封面上传.psd")
    app.open(fileRef);
    // 确保有活动文档
    if (app.documents.length > 0) {
        var doc = app.activeDocument;
        var layers = doc.layers;
        var metadata = readJSONFile(currentFolder + "基本信息数据.json");

        // 确保读取的 JSON 数据有效
        if (metadata) {
            layers.getByName("日期").textItem.contents = metadata.date;
            $.writeln(metadata.date)
        } else {
            $.writeln("读取 JSON 数据时出错");
        }
        var position = [1024, 380];
        var size = [100, 100];
        var relativeObject = layers.getByName("日刊虚拟歌手");
        var insertionLocation = ElementPlacement.PLACEBEFORE;
        var thumbLayer = importImage(currentFolder + '其他图片\\最高新曲封面.png', "封面", layers, relativeObject, insertionLocation, size, position);
        savePic(doc, currentFolder + '其他图片\\封面上传.png');
        doc.close(SaveOptions.SAVECHANGES);
    } else {
        $.writeln("没有活动文档");
    }
}

thumbnailUpload();