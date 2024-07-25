#include 'json2.js'

var currentFolder = "D:\\自制\\视频\\B站日V日刊\\"
var contain = 20;
var extend = 100;

// 自定义的对象，已弃用
function MyTextLayer(textLayer) {
    this.textLayer = textLayer;
    this.textItem = textLayer.textItem; // 简化访问，存储 textItem

    this.setFormattedText = function(contents, size, font) {
        if (contents !== undefined) {
            this.textItem.contents = contents; // 直接操作 textItem
        }
        if (size !== undefined) {
            this.textItem.size = size;
        }
        if (font !== undefined) {
            this.textItem.font = font;
        }
    };

    this.resizeText = function(width) {
        this.textItem.horizontalScale = 90; // 初始设置
        var textBounds = this.textLayer.bounds;
        var textWidth = textBounds[2] - textBounds[0]; // 计算文本图层的宽度
        if (textWidth > width) {
            var scalePercent = (width / textWidth) * 90; // 使用 90% 的比例缩放文本
            this.textItem.horizontalScale = scalePercent; // 修改 horizontalScale
        }
    };

    this.setColor = function(color) {
        var newColor = new SolidColor();
        var colors = {
            'red': [255, 0, 0],
            'green': [0, 255, 0],
            'blue': [0, 0, 255],
            'black': [0, 0, 0]
        };
        newColor.rgb.red = colors[color][0];
        newColor.rgb.green = colors[color][1];
        newColor.rgb.blue = colors[color][2];
        this.textItem.color = newColor;
    }
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

function savePic(doc, path) {
    var pngFile = new File(path); // 修改为你的目标路径和文件名
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
        var scalePercent = width / textWidth * 9 / 10 * 100;
        textLayer.textItem.horizontalScale = scalePercent;
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

        // 复制图像内容到剪贴板
        image.selection.selectAll();
        image.selection.copy();
        image.close(SaveOptions.DONOTSAVECHANGES);

        // 粘贴图像到目标文档
        targetDoc.paste();
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
    var colors = {
        'red': [255, 0, 0],
        'green': [0, 255, 0],
        'blue': [0, 0, 255],
        'black': [0, 0, 0]
    };
    newColor.rgb.red = colors[color][0];
    newColor.rgb.green = colors[color][1];
    newColor.rgb.blue = colors[color][2];
    textItem.color = newColor;
}

function fillDataExtend(songData, layers, keys) {
    layers.getByName("数值").textItem.contents = comma(songData[keys[0]]);
    layers.getByName("位次").textItem.contents = songData[keys[1]] + '位';
    if (songData[keys[1]] === Math.min(songData.view_rank, songData.favorite_rank, songData.coin_rank, songData.like_rank)) {
        setColor(layers.getByName("位次").textItem, 'red');
    } else {
        setColor(layers.getByName("位次").textItem, 'black');
    }
}

function fillData(songData, layers, keys) {
    layers.getByName("数值").textItem.contents = comma(songData[keys[0]]);
    layers.getByName("修正").textItem.contents = '×' + songData[keys[1]].toFixed(2);
    if (
        (keys[0] === 'view' && songData[keys[1]] < 1) ||
        (keys[0] === 'favorite' && songData[keys[1]] < 10) ||
        (keys[0] === 'coin' && songData[keys[1]] < 20) ||
        (keys[0] === 'like' && songData[keys[1]] < 2)
    ) {
        $.writeln("blue");
        setColor(layers.getByName("修正").textItem, 'blue');
    } else {
        $.writeln("black");
        setColor(layers.getByName("修正").textItem, 'black');
    }
    layers.getByName("位次").textItem.contents = songData[keys[2]] + '位';
    if (songData[keys[2]] === Math.min(songData.view_rank, songData.favorite_rank, songData.coin_rank, songData.like_rank)) {
        setColor(layers.getByName("位次").textItem, 'red');
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