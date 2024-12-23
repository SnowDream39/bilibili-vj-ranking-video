#include 'ps.jsx'

function extendTitle() {
    var mode = judgeMode();
    var fileRef = new File(currentFolder + "其他图片\\副榜.psd");
    app.open(fileRef);
    // 确保有活动文档
    if (app.documents.length > 0) {
        var doc = app.activeDocument;
        var layers = doc.layers;
        var metadata = readJSONFile(currentFolder + "基本信息数据.json");

        // 确保读取的 JSON 数据有效
        if (metadata) {
            layers.getByName("extend").textItem.contents = extend;
            setFormattedText(textLayer = layers.getByName("BGM"), contents = metadata.ED_title, size = undefined, font = "SourceHanSansSC-Bold", width=1200);
            layers.getByName("BGM").textItem.contents = "BGM：" + metadata.ED_title;
            savePic(doc, currentFolder + '其他图片\\副榜.png');
            doc.close(SaveOptions.SAVECHANGES);
        } else {
            $.writeln("读取 JSON 数据时出错");
        } 
    } else {
        $.writeln("没有活动文档");
    }
}

extendTitle();