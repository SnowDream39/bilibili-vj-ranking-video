#include 'pr.jsx'
var contain = 14;
var name = "PICKUP"
var clipLength = 20

var metadata = readJSONFile(currentFolder + '基本信息数据.json');

var sequenceName = name;
var project = app.project;
var rootItem = project.rootItem;

var sequence = project.createNewSequence(sequenceName, "standard");

var allData = readJSONFile(currentFolder + "数据.json");
var newData = readJSONFile(currentFolder + '新曲数据.json');


var audioTracks = sequence.audioTracks;
var musicTrack = audioTracks[0];
var songTrack = audioTracks[1];
var videoTracks = sequence.videoTracks;
var imageTrack = videoTracks[0];
var videoTrack = videoTracks[1];

var mainImageBin = refreshBin(rootItem, name + '图片');
var otherImageBin = refreshBin(rootItem, '其他图片');
var mainVideoBin = refreshBin(rootItem, name + '视频');

var videoTime = new Time();
var audioTime = new Time();

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

    for (var i = startRank; i < endRank; i++) {
        var bvid = jsonGet(data, 'rank', i).bvid;
        videoFiles.push(currentFolder + '视频\\' + bvid + '.mp4');
        lengths.push(clipLength); 
        videoData.push(data[i - 1]);
        imageFiles.push(currentFolder + name + '图片\\' + i + '.png');
    }
    var tempTime = new Time();
    tempTime.ticks = time.ticks;
    importVideosToTrack(videoFiles, videoBin, videoTrack, lengths, tempTime, videoData);
    var videoTime = importVideosToTrack(imageFiles, imageBin, imageTrack, lengths, time, null);

    return videoTime;
}




// 导入主榜
videoTime = makeRanks(1, contain+1, videoTrack, imageTrack, mainVideoBin, mainImageBin, name, videoTime, allData);
audioTime.ticks = videoTime.ticks;


// 设置视频位置和缩放
var clips = videoTrack.clips;
for (var i = 0; i < clips.numItems; i++) {
    var clip = clips[i];
    videoSizeFit(clip, [1449.1, 815.1], [0.3885, 0.3943]);
}

// 音频关键帧处理
var clips = songTrack.clips;
for (var i = 0; i < clips.numItems; i++) {
    var clip = clips[i];
    audioFadeout(clip, 1);
}
project.save();

