#include 'ps.jsx'


function thumbnail() {
    var mode = judgeMode();
    if(mode === 'daily'){
        var name = '日刊虚拟歌手';
    }

    var inputFiles = [ new File(currentFolder + "其他图片\\日刊\\4比3封面.psd"),  new File(currentFolder + "其他图片\\日刊\\16比9封面.psd") ];
    var thumbnails = [currentFolder + '其他图片\\最高新曲封面4比3.png', currentFolder + '其他图片\\最高新曲封面16比9.png']
    var outputFiles = [currentFolder + '其他图片\\4比3封面.png', currentFolder + '其他图片\\16比9封面.png']


    for(var i=0; i<inputFiles.length; i++){

        app.open(inputFiles[i]);
        // 确保有活动文档
        if (app.documents.length > 0) {
            var doc = app.activeDocument;
            var layers = doc.layers;
            layers.getByName('标题').layers[0].textItem.contents = name;
            var metadata = readJSONFile(currentFolder + "基本信息数据.json");

            // 确保读取的 JSON 数据有效
            if (metadata) {
                var weekday = metadata.weekday;

                var themes = ['周日主题色', '周一主题色', '周二主题色', '周三主题色', '周四主题色', '周五主题色', '周六主题色'];
                var colors = ['547c9b','934c70','e06445','595959','3494a8','bfbfbf','cc8800'];
                for (var j = 0; j < themes.length; j++) {
                    if (j == weekday%7) {
                        layers.getByName(themes[j]).visible = true;
                        setColor(layers.getByName("期数").textItem, colors[j]);
                    } else {
                        layers.getByName(themes[j]).visible = false;
                    }
                }
                layers.getByName("年").textItem.contents = metadata.year;
                layers.getByName("月").textItem.contents = padNumber(metadata.month, 2) + '/';
                layers.getByName("日").textItem.contents = padNumber(metadata.day, 2);
                layers.getByName("总期数").textItem.contents = "总第"+ padNumber(metadata.total_phase, 5) + "期";
                layers.getByName("期数").textItem.contents = padNumber(metadata.phase, 3);
                $.writeln(metadata.date);
            } else {
                $.writeln("读取 JSON 数据时出错");
            }
            var position = [0, 0];
            var size = [100, 100];
            var relativeObject = layers.getByName("周三主题色");
            var insertionLocation = ElementPlacement.PLACEAFTER;
            var thumbLayer = importImage(thumbnails[i], "封面", layers, relativeObject, insertionLocation, size, position);
            layers.getByName("竖屏省流版").visible = false;
            savePic(doc, outputFiles[i]);
            doc.close(SaveOptions.SAVECHANGES);
        } else {
            $.writeln("没有活动文档");
        }

    }
}

thumbnail();