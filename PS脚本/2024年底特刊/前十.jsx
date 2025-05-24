#include '../ps.jsx'

var contain = 10;
var fileRef = new File(currentFolder + "其他图片\\2024年终\\前十.psd");
app.open(fileRef);
// 确保有活动文档
if (app.documents.length > 0) {
    var doc = app.activeDocument;
    var layers = doc.layers;
    var data = readJSONFile(currentFolder + "数据.json");

    // 确保读取的 JSON 数据有效
    if (data) {
        for (var i=0; i<contain; i++){
            layers.getByName("排名").textItem.contents = i + 1;
            layers.getByName("分差").textItem.contents = comma(data[i].point - data[i+1].point);
            
            savePic(doc, currentFolder + '其他图片\\2024年终\\' + (i+1) + '.png');
        }
        // doc.close(SaveOptions.SAVECHANGES);
    } else {
        $.writeln("读取 JSON 数据时出错");
    } 
} else {
    $.writeln("没有活动文档");
}

