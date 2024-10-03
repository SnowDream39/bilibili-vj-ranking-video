#include 'ps.jsx'


function fillStats(layers, name, stat){
    var mode = judgeMode();
    layers.getByName('名称').textItem.contents = name;
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



function statistics1() {
    var mode = judgeMode();
    var fileRef = new File(currentFolder + "其他图片\\统计数据.psd")
    app.open(fileRef);
    // 确保有活动文档
    if (app.documents.length > 0) {
        var doc = app.activeDocument;
        var layers = doc.layers;
        var stats = readJSONFile(currentFolder + "统计.json");

        // 确保读取的 JSON 数据有效
        if (stats) {
            if (mode === 'daily'){
                layers.getByName('标题').textItem.contents = '今日榜单统计数据';
                fillStats(layers.getByName('第一档分数').layers, "10万分以上          首", stats.high_points['10w']);
                fillStats(layers.getByName('第二档分数').layers, "2万分以上          首", stats.high_points['2w']);
                fillStats(layers.getByName('第三档分数').layers, "1万分以上          首", stats.high_points['1w']);
                fillStats(layers.getByName('主榜新曲数').layers, "主榜5日以内新曲          首", stats.new_songs.main);
                fillStats(layers.getByName('全榜新曲数').layers, "全榜5日以内新曲          首", stats.new_songs.extend);
            } else if (mode === 'weekly'){
                layers.getByName('标题').textItem.contents = '本周榜单统计数据';
                fillStats(layers.getByName('第一档分数').layers, "50万分以上          首", stats.high_points['50w']);
                fillStats(layers.getByName('第二档分数').layers, "10万分以上          首", stats.high_points['10w']);
                fillStats(layers.getByName('第三档分数').layers, "5万分以上          首", stats.high_points['5w']);
                fillStats(layers.getByName('主榜新曲数').layers, "主榜2周以内新曲          首", stats.new_songs.main);
                fillStats(layers.getByName('全榜新曲数').layers, "全榜2周以内新曲          首", stats.new_songs.extend);
            } else if (mode === 'monthly'){
                layers.getByName('标题').textItem.contents = '本周榜单统计数据';
                fillStats(layers.getByName('第一档分数').layers, "100万分以上          首", stats.high_points['100w']);
                fillStats(layers.getByName('第二档分数').layers, "50万分以上          首", stats.high_points['50w']);
                fillStats(layers.getByName('第三档分数').layers, "10万分以上          首", stats.high_points['10w']);
                fillStats(layers.getByName('主榜新曲数').layers, "主榜本月新曲          首", stats.new_songs.main);
                fillStats(layers.getByName('全榜新曲数').layers, "全榜本月新曲          首", stats.new_songs.extend);
            }

            fillStats(layers.getByName('主榜起分').layers, "主榜起分", stats.start_points.main);
            fillStats(layers.getByName('新曲榜起分').layers, "新曲榜起分", stats.start_points.new);
            fillStats(layers.getByName('副榜起分').layers, "副榜起分", stats.start_points.extend);
            var metadata = readJSONFile(currentFolder + '基本信息数据.json');
            savePic(doc, currentFolder + '其他图片\\统计数据.png');
            // doc.close(SaveOptions.SAVECHANGES);
        } else {
            $.writeln("读取 JSON 数据时出错");
        } 
    } else {
        $.writeln("没有活动文档");
    }
}

statistics1();