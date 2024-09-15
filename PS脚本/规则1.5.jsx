#include 'ps.jsx'

// var MODE = 'weekly';

function extendTitle15() {
    if (MODE == 'weekly'){
        var fileRef = new File(currentFolder + "其他图片\\周刊\\规则1.5.psd");
    }
    app.open(fileRef);
    // 确保有活动文档
    if (app.documents.length > 0) {
        var doc = app.activeDocument;
        var layers = doc.layers;
        var metadata = readJSONFile(currentFolder + "基本信息数据.json");

        // 确保读取的 JSON 数据有效
        if (metadata) {
            layers.getByName("时间范围").textItem.contents = metadata.time_range;
            savePic(doc, currentFolder + '其他图片\\规则1.5.png');
            doc.close(SaveOptions.SAVECHANGES);
        } else {
            $.writeln("读取 JSON 数据时出错");
        } 
    } else {
        $.writeln("没有活动文档");
    }
}

extendTitle15();