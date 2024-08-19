#include 'ps.jsx'

function fillStats(layers, stat){
    $.writeln('开始')
    layers.getByName('数值').textItem.contents = comma(stat.today);

    textItem = layers.getByName('变化').textItem;
    change = stat.change;
    if (stat.change > 0) {
        textItem.contents = '（+' + comma(change) + '）';
        setColor(textItem, 'ff0020');
    } else if (stat.change == 0) {
        textItem.contents = '（0）';
        setColor(textItem, 'grey');
    } else {
        textItem.contents = '（-' + comma(-change) + '）';
        setColor(textItem, '0aab62');
    }
}

function fillTops(layers, tops){
    for (var i=0; i<tops.length; i++){
        layers.getByName(i+1).textItem.contents = (i+1) + '.' + tops[i].name + '（' + tops[i].count + '）';
    }

    for (var i=2; i>=tops.length; i--){
        layers.getByName(i+1).textItem.contents = '';
    }
}


function statistics() {
    var fileRef = new File(currentFolder + "其他图片\\统计.psd")
    app.open(fileRef);
    // 确保有活动文档
    if (app.documents.length > 0) {
        var doc = app.activeDocument;
        var layers = doc.layers;
        var stats = readJSONFile(currentFolder + "统计.json");

        // 确保读取的 JSON 数据有效
        if (stats) {
            fillStats(layers.getByName('10万分以上').layers, stats['10w']);
            fillStats(layers.getByName('2万分以上').layers, stats['2w']);
            fillStats(layers.getByName('1万分以上').layers, stats['1w']);
            fillStats(layers.getByName('主榜起分').layers, stats.main_point);
            fillStats(layers.getByName('新曲榜起分').layers, stats.new_point);
            fillStats(layers.getByName('副榜起分').layers, stats.extend_point);
            fillStats(layers.getByName('主榜新曲数').layers, stats.main_news);
            fillStats(layers.getByName('全榜新曲数').layers, stats.extend_news);

            fillTops(layers.getByName('歌姬排名').layers, stats.top_vocals);
            fillTops(layers.getByName('引擎排名').layers, stats.top_synthesizers);

            savePic(doc, currentFolder + '其他图片\\统计.png');
            doc.close(SaveOptions.SAVECHANGES);
        } else {
            $.writeln("读取 JSON 数据时出错");
        } 
    } else {
        $.writeln("没有活动文档");
    }
}

statistics();