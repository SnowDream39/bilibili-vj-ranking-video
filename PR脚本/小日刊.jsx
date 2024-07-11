#include 'pr.jsx'

var sequenceName = "小日刊";
var project = app.project;
var rootItem = project.rootItem;

var sequences = project.sequences;
for (var i = 0; i < sequences.length; i++) {
    project.deleteSequence(sequences[i]);
}
var sequence = project.createNewSequence(sequenceName, "standard");

var allData = readJSONFile(currentFolder + "数据.json");
var newData = readJSONFile(currentFolder + '新曲数据.json');
var metadata = readJSONFile(currentFolder + '基本信息数据.json');

var audioTracks = sequence.audioTracks;
var musicTrack = audioTracks[0];
var songTrack = audioTracks[1];
var videoTracks = sequence.videoTracks;
var imageTrack = videoTracks[0];
var videoTrack = videoTracks[1];

var cutBin = refreshBin(rootItem, '截取片段用视频');
var newImageBin = refreshBin(rootItem, '新曲榜图片');
var shortImageBin = refreshBin(rootItem, '省流版图片');
var otherImageBin = refreshBin(rootItem, '其他图片');
var newVideoBin = refreshBin(rootItem, '新曲榜视频');

var videoTime = new Time();
var audioTime = new Time();

// 新曲榜
videoTime = makeRanks(news, 0, videoTrack, imageTrack, newVideoBin, shortImageBin, '省流版', videoTime, newData);
audioTime.ticks = videoTime.ticks;

// 设置视频位置和缩放
var clips = videoTrack.clips;
for (var i = 0; i < clips.numItems; i++) {
    var clip = clips[i];
    videoSizeFit(clip, [1080, 607.5], [0.5, 0.2745]);
}

// 音频关键帧处理
var clips = songTrack.clips;
for (var i = 0; i < clips.numItems; i++) {
    var clip = clips[i];
    audioFadeout(clip, 1);
}


