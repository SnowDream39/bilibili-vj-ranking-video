#include '../pr.jsx'

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
        var bvid = data[i].bvid;
        videoFiles.push(currentFolder + '视频\\' + bvid + '.mp4');
        lengths.push(20); 
        videoData.push(data[i]);
        imageFiles.push(currentFolder + name + '图片\\' + (i + 1) + '.png');
    }
    var tempTime = new Time();
    tempTime.ticks = time.ticks;
    importVideosToTrack(videoFiles, videoBin, videoTrack, lengths, tempTime, videoData);
    var videoTime = importVideosToTrack(imageFiles, imageBin, imageTrack, lengths, time, null);

    project.save();
    return videoTime;
}

var contain = 15;

var metadata = readJSONFile(currentFolder + '基本信息数据.json');

var sequenceName = "历年第一";
var project = app.project;
var rootItem = project.rootItem;

var sequences = project.sequences;
var sequence = project.createNewSequence(sequenceName, "standard");

var allData = readJSONFile(currentFolder + "数据.json");
var newData = readJSONFile(currentFolder + '新曲数据.json');


var audioTracks = sequence.audioTracks;
var musicTrack = audioTracks[0];
var songTrack = audioTracks[1];
var videoTracks = sequence.videoTracks;
var imageTrack = videoTracks[0];
var videoTrack = videoTracks[1];

var cutBin = refreshBin(rootItem, '截取片段用视频');
var mainImageBin = refreshBin(rootItem, '历年第一图片');
var subImageBin = refreshBin(rootItem, '副榜图片');
var newImageBin = refreshBin(rootItem, '新曲榜图片');
var otherImageBin = refreshBin(rootItem, '其他图片');
var mainVideoBin = refreshBin(rootItem, '历年第一视频');
var newVideoBin = refreshBin(rootItem, '新曲榜视频');
var musicBin = refreshBin(rootItem, '音乐');

var videoTime = new Time();
var audioTime = new Time();

// 导入主榜
videoTime = makeRanks(0, contain, videoTrack, imageTrack, mainVideoBin, mainImageBin, '历年第一', videoTime, allData);
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

