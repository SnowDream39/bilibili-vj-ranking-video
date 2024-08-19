#include 'json2.js'

var currentFolder = "D:\\自制\\视频\\B站日V日刊\\";
var contain = 20;
var extend = 100;
var news = 10;
var mainSeconds = 20;
var ticks = 254016000000;


// 读取 JSON 文件的函数
function readJSONFile(filepath) {
    var file = new File(filepath);
    if (file.exists) {
        file.encoding = "UTF-8";
        file.open("r");
        var content = file.read();
        file.close();
        return JSON.parse(content);
    } else {
        $.writeln("文件不存在: " + filepath);
        return null;
    }
}

function writeJSONFile(filepath, content) {
    var file = new File(filepath);
    file.encoding = "UTF-8";
    file.open("w");
    file.write(JSON.stringify(content, null, 4));
    file.close();
}

function getByName(bin, name) {
    if (bin) {
        for (var i = 0; i < bin.children.numItems; i++) {
            var item = bin.children[i];
            if (item.name === name) {
                return item;
            }
        }
    }

    return null; // 如果未找到则返回 null
}

function jsonGet(data, searchKey, searchValue) {
    for (var i = 0; i < data.length; i++) {
        if (data[i][searchKey] === searchValue) {
            return data[i];
        }
    }
    return null;
}

function sum(items) {
    var s = 0;
    for (var i = 0; i < items.length; i++) {
        s += items[i];
    }
    return s;
}

function importClips(bin, items, lengths, track, time, type) {
    for (var i = 0; i < items.length; i++) {
        var currentItem = getByName(bin, items[i]);
        currentItem.setOutPoint(lengths[i] * ticks, type);
        // 将图片加入到序列
        track.overwriteClip(currentItem, String(time.ticks));
        var trackItem = track.clips[track.clips.length - 1];
        time.seconds += lengths[i];
        trackItem.end = time;
    }
    return time;
}

function refreshBin(fatherBin, name) {
    var newBin = getByName(fatherBin, name);
    if (newBin) {
        newBin.deleteBin();
    }
    return fatherBin.createBin(name);
}

function audioFadeout(clip, seconds) {
    var components = clip.components;
    var volume = components[0];
    var properties = volume.properties;
    var level = properties[1];
    level.setTimeVarying(true);
    var key1 = new Time();
    key1.seconds = clip.outPoint.seconds - seconds;

    level.addKey(key1);
    level.setValueAtKey(key1, 0.1778);
    level.addKey(clip.outPoint.ticks);
    level.setValueAtKey(clip.outPoint.ticks, 0.0056);
}


function videoSizeFit(clip, size, _position) {
    var sourceVideo = clip.projectItem;
    var projectItemMetadata = sourceVideo.getProjectColumnsMetadata();
    projectItemMetadata = JSON.parse(projectItemMetadata);
    var clipSize = jsonGet(projectItemMetadata, "ColumnName", "视频信息")['ColumnValue'].split(" ")
    var horizontalRes = clipSize[0];
    var verticalRes = clipSize[2];
    var components = clip.components;
    var motion = components[1];
    var properties = motion.properties;
    var position = properties[0];
    var resize = properties[1];
    position.setValue(_position);

    if (horizontalRes / verticalRes > size[0] / size[1]) {
        // 视频过于宽
        resize.setValue(size[0] / horizontalRes * 100);
    } else {
        // 视频过于高
        resize.setValue(size[1] / verticalRes * 100);
    }

}

function importVideosToTrack(files, bin, track, lengths, time, data) {
    project.importFiles(files, false, bin, false);

    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        //导入到工程
        var currentFile = getByName(bin, file.split('\\').pop());

        if (data && data[i]) {
            currentFile.name = data[i].rank + '.mp4';
            var inPoint = data[i].inPoint;
            currentFile.setInPoint(inPoint, 4);
            var outPoint = data[i].outPoint;
            currentFile.setOutPoint(outPoint, 4);
        }
        //加入到序列
        $.writeln(track,currentFile,time.ticks);
        track.overwriteClip(currentFile, String(time.ticks));
        var trackItem = track.clips[track.clips.length - 1];
        time.seconds += lengths[i];
        trackItem.end = time;
    }
    return time;
}

function makeRanks(startRank, endRank, videoTrack, imageTrack, videoBin, imageBin, name, time, data) {
    var videoFiles = [];
    var lengths = [];
    var videoData = [];
    var imageFiles = [];
    $.writeln(data.length);
    if (data.length < startRank) {
        $.writeln(data.length);
        startRank = data.length - 1;
    }

    for (var i = startRank; i > endRank; i--) {
        var bvid = jsonGet(data, 'rank', i).bvid;
        videoFiles.push(currentFolder + '视频\\' + bvid + '.mp4');
        lengths.push(20); // Assuming a fixed length for each clip, adjust if necessary
        videoData.push(data[i - 1]);
        imageFiles.push(currentFolder + name + '图片\\' + i + '.png');
    }
    var tempTime = new Time();
    tempTime.ticks = time.ticks;
    importVideosToTrack(videoFiles, videoBin, videoTrack, lengths, tempTime, videoData);
    var videoTime = importVideosToTrack(imageFiles, imageBin, imageTrack, lengths, time, null);

    project.save();
    return videoTime;
}

