#include 'json2.js'
#include 'ps.jsx'

function fillChange(textItem, change){
    if (change>0) {
        textItem.contents = '（+' + comma(change) + ')';
        setColor(textItem, 'ff0020');
    } else if (change == 0) {
        textItem.contents = '（0）';
        setColor(textItem, 'grey');
    } else {
        textItem.contents = '（-' + comma(-change) + '）';
        setColor(textItem, '0aab62');
    }
}
function fillTops(topLayers, tops){
    for (var i=0; i<tops.length; i++){
        topLayers.getByName(i+1).visible = true;
        var layers = topLayers.getByName(i+1).layers;
        layers.getByName("排名").textItem.contents = tops[i].rank;
        layers.getByName("排名变化").visible = false;
        layers.getByName("名称").textItem.contents = tops[i].name;
        layers.getByName("数值").textItem.contents = tops[i].count;
        fillChange(layers.getByName("数值变化").textItem, tops[i].change);
    }

    for (var i=9; i>=tops.length; i--){
        topLayers.getByName(i+1).visible = false;
    }
}


function statistics2(){
    var fileRef = new File(currentFolder + "其他图片\\统计2.psd")
    app.open(fileRef);

    var doc = app.activeDocument;
    var layers = doc.layers;
    var stats = readJSONFile(currentFolder + '统计.json');

    if (stats){
        fillTops(layers.getByName("歌姬排名").layers,stats['top_vocals']);
        fillTops(layers.getByName("引擎排名").layers,stats['top_synthesizers']);

        savePic(doc, currentFolder + '其他图片\\统计2.png');
        doc.close(SaveOptions.SAVECHANGES);
    } else {
        $.writeln("读取 JSON 数据时出错");
    } 
}


statistics2();