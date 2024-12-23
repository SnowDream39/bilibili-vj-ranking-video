#include 'json2.js'

var currentFolder = "D:\\自制\\视频\\B站日V日刊\\"
var contain = 20;
var extend = 100; // 手动改
var TEMP_MODE = 'weekly'; //需要临时运行一个脚本的话修改此处

function judgeMode() {
    if (typeof MODE === 'undefined'){
        var newMode = TEMP_MODE;
    }else{
        var newMode = MODE;
    }
    return newMode
}


function readJSONFile(filepath) {
    var file = new File(filepath);
    if (file.exists) {
        file.open("r");
        var content = file.read();
        file.close();
        return JSON.parse(content);
    } else {
        $.writeln("文件不存在: " + filepath);
        return null;
    }
}

function comma(value) {
    value = String(value);
    var valueComma = '';
    for (var i = 1; i <= value.length; i++) {
        valueComma = value[value.length - i] + valueComma;
        if (i % 3 == 0 && i != value.length) {
            valueComma = ',' + valueComma;
        }
    }
    return valueComma;
}
function percent(value) {
    return String((value * 100)) + "%";
}

function savePic(doc, path) {
    var pngFile = new File(path); 
    // 保存选项
    var exportOptions = new ExportOptionsSaveForWeb();
    exportOptions.format = SaveDocumentType.PNG;
    exportOptions.PNG8 = false; // 使用PNG-24格式
    exportOptions.transparency = true;
    exportOptions.interlaced = false;
    exportOptions.quality = 100;
    // 导出为PNG文件
    doc.exportDocument(pngFile, ExportType.SAVEFORWEB, exportOptions);
}

function resizeText(textLayer, width) {
    textLayer.textItem.horizontalScale = 90;
    var textBounds = textLayer.bounds;
    var textWidth = textBounds[2] - textBounds[0]; // 计算文本图层的宽度
    if (textWidth > width) {
        var size = textLayer.textItem.size;
        var rate = width / textWidth;
        textLayer.textItem.size = size * ( rate / 2 + 0.5 );
        textLayer.textItem.baselineShift = - size * (1 - rate) / 4;
        var textBounds = textLayer.bounds;
        var textWidth = textBounds[2] - textBounds[0]; // 计算文本图层的宽度
        var scalePercent = width / textWidth * 90;
        textLayer.textItem.horizontalScale = scalePercent;
    } else {
        textLayer.textItem.baselineShift = 0;
    }
}

function movePosition(layer, x, y) {
    var bounds = layer.bounds;
    layer.translate(-bounds[0], -bounds[1]);
    layer.translate(x, y);
}

function importImage(filePath, name, layers, relativeObject, insertionLocation, size, position) {
    var file = new File(filePath);
    if (file.exists) {
        // 检查当前文档是否存在
        var targetDoc = app.activeDocument;
        if (!targetDoc) {
            $.writeln("No active document found.");
            return null;
        }

        // 移除同名图层
        for (var j = 0; j < layers.length; j++) {
            if (layers[j].name == name) {
                layers[j].remove();
                break; // 找到后移除一次即可跳出循环
            }
        }

        // 打开图像
        var image = open(file);
        if (!image) {
            $.writeln("Failed to open the image.");
            return null;
        }

        // 创建图像副本到目标文档 
        var curLayer = image.layers[0];
        curLayer.duplicate(relativeObject, insertionLocation);
        image.close(SaveOptions.DONOTSAVECHANGES);
        var changeLayer = targetDoc.activeLayer;

        // 检查是否成功粘贴
        if (!changeLayer) {
            $.writeln("Failed to paste the image.");
            return null;
        }

        // 调整图层大小
        changeLayer.resize(size[0], size[1]);
        changeLayer.name = name;
        // 移动图层到相对位置
        changeLayer.move(relativeObject, insertionLocation);

        // 移动图层到指定位置
        var x = position[0];
        var y = position[1];
        movePosition(changeLayer, x, y);

        return changeLayer;
    } else {
        $.writeln("File does not exist: " + filePath);
    }
    return null;
}

function setColor(textItem, color) {
    var newColor = new SolidColor();
    var presetColors = {
        'red': "ff0000",
        "green": "00ff00",
        'blue': "0000ff",
        'black': "000000",
        'grey': "808080"
    };
    if(presetColors.hasOwnProperty(color)){
        color = presetColors[color];
    }
    newColor.rgb.hexValue = color;
    textItem.color = newColor;
}

function fillDataExtend(songData, layers, keys) {
    if (keys[0] === 'coin' && songData['fixA'] != 1.0) {
        layers.getByName("数值").textItem.contents = comma(songData[keys[0]]) + '(×' + songData['fixA'].toFixed(2) + ')';
    } else {
        layers.getByName("数值").textItem.contents = comma(songData[keys[0]]);
    }
    layers.getByName("位次").textItem.contents = songData[keys[1]];
    if (songData[keys[1]] === Math.min(songData.view_rank, songData.favorite_rank, songData.coin_rank, songData.like_rank)) {
        setColor(layers.getByName("位次").textItem, 'e06445');
    } else {
        setColor(layers.getByName("位次").textItem, 'black');
    }
}

function fillData(songData, layers, keys) {
    if (keys[0] === 'coin' && songData['fixA'] != 1.0) {
        layers.getByName("数值").textItem.contents = comma(songData[keys[0]]) + '(×' + songData['fixA'].toFixed(2) + ')';
    } else {
        layers.getByName("数值").textItem.contents = comma(songData[keys[0]]);
    }
    layers.getByName("补正").textItem.contents = '×' + songData[keys[1]].toFixed(2);
    if (
        (keys[0] === 'view' && songData[keys[1]] < 1) ||
        (keys[0] === 'favorite' && songData[keys[1]] < 10) ||
        (keys[0] === 'coin' && songData[keys[1]] < 20) ||
        (keys[0] === 'like' && songData[keys[1]] < 2)
    ) {
        setColor(layers.getByName("补正").textItem, '3494a8');
    } else {
        setColor(layers.getByName("补正").textItem, 'black');
    }
    layers.getByName("位次").textItem.contents = songData[keys[2]];
    if (songData[keys[2]] === Math.min(songData.view_rank, songData.favorite_rank, songData.coin_rank, songData.like_rank)) {
        setColor(layers.getByName("位次").textItem, 'e06445');
    } else {
        setColor(layers.getByName("位次").textItem, 'black');
    }
}

function setFormattedText(textLayer, contents, size, font, width) {
    if (contents !== undefined) {
        textLayer.textItem.contents = contents;
    }
    if (font !== undefined) {
        textLayer.textItem.font = font;
    }
    if (size !== undefined) {
        textLayer.textItem.size = size;
    }

    if (width !== undefined) {
        resizeText(textLayer, width);
    }
}

function padNumber(num, length) {
    var str = num.toString();
    while (str.length < length) {
        str = '0' + str;
    }
    return str;
}



function fillSeperatedRanks(layers, ranks, mode) {
    if (mode == 'daily'){
        layers.getByName("日排名").visible = false;
        layers.getByName("周排名").visible = false;
        return 0
    } else if (mode == 'weekly'){
        layers.getByName("日排名").visible = true;
        layers.getByName("周排名").visible = false;
        layers = layers.getByName("日排名").layers;
    } else if (mode == 'monthly'){
        layers.getByName("日排名").visible = false;
        layers.getByName("周排名").visible = true;
        layers = layers.getByName("周排名").layers;
    }
    for(var i = 0; i < ranks.length; i++){
        var layer = layers[i];
        var rank = ranks[i];
        var textItem = layer.textItem;
        textItem.contents = rank;
        if(rank >= 1000){
            textItem.size = 24;
            textItem.baselineShift = 4;
        } else if(rank >= 100){
            textItem.size = 30;
            textItem.baselineShift = 2;
        } else {
            textItem.size = 36;
            textItem.baselineShift = 0;
        }
    }
}


function fillSongInfo(layers, songData, mode, part) {
    
    setFormattedText(textLayer = layers.getByName("标题"), contents = songData.title, size = 54, font = "SourceHanSansCN-Bold", width=1430);
    setFormattedText(textLayer = layers.getByName("作者"), contents = songData.author, size = 48, font = "SourceHanSansCN-Bold", width=750);
    setFormattedText(textLayer = layers.getByName("歌手"), contents = songData.vocal, size = 36, font = "SourceHanSansCN-Bold", width=750);
    setFormattedText(textLayer = layers.getByName("引擎"), contents = songData.synthesizer, size = 36, font = "SourceHanSansCN-Bold", width=750);

    layers.getByName("BV号").textItem.contents = songData.bvid;
    layers.getByName("投稿时间").textItem.contents = songData.pubdate.substring(0, 16);
    layers.getByName("类型").textItem.contents = songData.type;
    if (songData.page == 1){
        layers.getByName("时长").textItem.contents = songData.duration; 
    }else{
        layers.getByName("时长").textItem.contents = songData.duration + "/" + songData.page + "P";
    }

    if (songData.copyright === 1){
        var contents = "作者投稿";
    } else {
        var contents = "搬运：" + songData.uploader;
    }
    setFormattedText(textLayer = layers.getByName("copyright"), contents = contents, size = 36, font = "SourceHanSansCN-Bold", width=600);
    if (mode != 'monthly' && part == 'main') {
        layers.getByName("入榜次数").visible = true;
        layers.getByName("入榜次数").textItem.contents = "入榜次数：" + songData.count;
    } else {
        layers.getByName("入榜次数").visible = false;
    }
} 

function fillSongInfoExtend (layers, songData, mode) {
    setFormattedText(textLayer = layers.getByName("标题"), contents = songData.title, size=42.82, font = "SourceHanSansCN-Bold", width = 1080);
    fillVocalColors(layers.getByName("歌手颜色").layers, songData.vocal_colors);

    if (mode == "daily" || mode == "daily-text" || mode == "weekly") {
        setFormattedText(textLayer=layers.getByName("作者"), contents = songData.author, size = 31.14, font = undefined, width=300);
        layers.getByName("上榜次数").visible = true;
        layers.getByName("上榜次数").textItem.contents = "上榜次数：" + songData.count;
    } else if (mode == "monthly") {
        setFormattedText(textLayer=layers.getByName("作者"), contents = songData.author, size = 31.14, font = undefined, width=600);
        layers.getByName("上榜次数").visible = false;
    }
    layers.getByName("BV号").textItem.contents = songData.bvid;
    layers.getByName("投稿时间").textItem.contents = songData.pubdate.substring(0, 16);



}

function fillBeforeRank (layers, songData, mode){
    var rankLayers = layers.getByName("上期排名").layers;
    var pointLayers = layers.getByName("上期得分").layers;
    rankLayers.getByName("变化平").visible = false;
    rankLayers.getByName("变化升").visible = false;
    rankLayers.getByName("变化降").visible = false;
    if (songData.change == "new") {
        rankLayers.getByName("上期排名").textItem.contents = "";
        rankLayers.getByName("上期").visible = false;
        rankLayers.getByName("new").visible = true;
        layers.getByName("上期得分").visible = false;
    } else {
        rankLayers.getByName("上期").visible = true;
        rankLayers.getByName("new").visible = false;
        layers.getByName("上期得分").visible = true;
        if (songData.change == "up") {
            rankLayers.getByName("变化升").visible = true;
        } else if (songData.change == "cont") {
            rankLayers.getByName("变化平").visible = true;
        } else if (songData.change == "down") {
            rankLayers.getByName("变化降").visible = true;
        }

        if (songData.point_before == 0 || songData.point_before == "--") {
            rankLayers.getByName("上期排名").textItem.contents = "--";
            pointLayers.getByName("上期得分").textItem.contents = "--";
            pointLayers.getByName("RATE").textItem.contents = "--        ";
        } else {
            rankLayers.getByName("上期排名").textItem.contents = songData.rank_before;
            pointLayers.getByName("上期得分").textItem.contents = comma(songData.point_before);
            pointLayers.getByName("RATE").textItem.contents = percent(songData.rate);
        }
    }
}

function fillBeforeRankExtend(layers, songData, mode){

    var changeLayers = layers.getByName("变化").layers;
    changeLayers.getByName("变化平").visible = false;
    changeLayers.getByName("变化升").visible = false;
    changeLayers.getByName("变化降").visible = false;
    if (songData.change == "new") {
        layers.getByName("上期排名").textItem.contents = "";
        layers.getByName("上期").visible = false;
        layers.getByName("new").visible = true;
        changeLayers.getByName("变化升").visible = true;
    } else {
        layers.getByName("上期").visible = true;
        layers.getByName("new").visible = false;
        if (songData.change == "up") {
            changeLayers.getByName("变化升").visible = true;
        } else if (songData.change == "cont") {
            changeLayers.getByName("变化平").visible = true;
        } else if (songData.change == "down") {
            changeLayers.getByName("变化降").visible = true;
        }

        if (songData.point_before == 0) {
            layers.getByName("上期排名").textItem.contents = "--";
        } else {
            layers.getByName("上期排名").textItem.contents = songData.rank_before;
        }
    }

}

function fillVocalColors(layers, colors) {
    var length = colors.length;
    for(var i=0; i<6 && i<length; i++) {
        layers[i].visible = true;
        setColorOfFillLayer(layers[i], colors[i]);
    }
    for(var i=length; i<6; i++) {
        layers[i].visible = false;
    }

}

// https://community.adobe.com/t5/photoshop-ecosystem-discussions/ps-script-change-layer-color/m-p/2577577
function setColorOfFillLayer(layer, color) {
    app.activeDocument.activeLayer = layer;
    var sColor = new SolidColor;
    sColor.rgb.hexValue = color;
    var desc = new ActionDescriptor();
        var ref = new ActionReference();
        ref.putEnumerated( stringIDToTypeID('contentLayer'), charIDToTypeID('Ordn'), charIDToTypeID('Trgt') );
    desc.putReference( charIDToTypeID('null'), ref );
        var fillDesc = new ActionDescriptor();
            var colorDesc = new ActionDescriptor();
            colorDesc.putDouble( charIDToTypeID('Rd  '), sColor.rgb.red );
            colorDesc.putDouble( charIDToTypeID('Grn '), sColor.rgb.green );
            colorDesc.putDouble( charIDToTypeID('Bl  '), sColor.rgb.blue );
        fillDesc.putObject( charIDToTypeID('Clr '), charIDToTypeID('RGBC'), colorDesc );
    desc.putObject( charIDToTypeID('T   '), stringIDToTypeID('solidColorLayer'), fillDesc );
    executeAction( charIDToTypeID('setd'), desc, DialogModes.NO );
}