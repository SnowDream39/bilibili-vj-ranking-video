#include '../pr.jsx'
var contain = 200;

var metadata = readJSONFile(currentFolder + '基本信息数据.json');

var sequenceName = "特刊";
var project = app.project;
var rootItem = project.rootItem;

var sequences = project.sequences;
for (var i = 0; i < sequences.length; i++) {
    project.deleteSequence(sequences[i]);
}
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
var mainImageBin = refreshBin(rootItem, '主榜图片');
var subImageBin = refreshBin(rootItem, '副榜图片');
var newImageBin = refreshBin(rootItem, '新曲榜图片');
var otherImageBin = refreshBin(rootItem, '其他图片');
var mainVideoBin = refreshBin(rootItem, '主榜视频');
var newVideoBin = refreshBin(rootItem, '新曲榜视频');
var musicBin = refreshBin(rootItem, '音乐');

var videoTime = new Time();
var audioTime = new Time();

// 导入主榜
videoTime = makeRanks(contain, 0, videoTrack, imageTrack, mainVideoBin, mainImageBin, '总排行', videoTime, allData);
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

