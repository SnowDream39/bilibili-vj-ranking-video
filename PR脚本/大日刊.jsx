#include 'pr.jsx'

var metadata = readJSONFile(currentFolder + '基本信息数据.json');

var sequenceName = "大日刊";
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

// 开头
var openingImages = ["封面.png", "规则1.png", "规则2.png", "规则3.png", "新曲榜.png"];
var openingLength = [3, 5, 5, 5, 3];

for (var i = 0; i < openingImages.length; i++) {
    project.importFiles([currentFolder + "其他图片\\" + openingImages[i]], false, otherImageBin, false);
}

importClips(otherImageBin, openingImages, openingLength, imageTrack, videoTime, 1);

var musicFiles = [currentFolder + '视频\\' + metadata.OP_bvid + '.mp4'];
project.importFiles(musicFiles, false, musicBin, false);
var currentMusic = getByName(musicBin, metadata.OP_bvid + '.mp4');
currentMusic.setOutPoint('0',1)
currentMusic.setOutPoint(String(sum(openingLength)*ticks),2);
musicTrack.overwriteClip(currentMusic, audioTime.ticks);
audioTime.seconds = sum(openingLength);
var clip = musicTrack.clips[0];
audioFadeout(clip, 3);

// 新曲榜
videoTime = makeRanks(news, 0, videoTrack, imageTrack, newVideoBin, newImageBin, '新曲榜', videoTime, newData);
audioTime.ticks = videoTime.ticks;

// 导入主榜图片
var endingImages = ["主榜.png"];
for (var i = 0; i < endingImages.length; i++) {
    project.importFiles([currentFolder + "其他图片\\" + endingImages[i]], false, otherImageBin, false);
}
var endingLength = [3];
videoTime = importClips(otherImageBin, endingImages, endingLength, imageTrack, videoTime, 1);
audioTime.ticks = videoTime.ticks;

var topNewSongClip = songTrack.clips[songTrack.clips.length-1];
topNewSongClip.end = audioTime.ticks;
var time = new Time();
time.seconds = topNewSongClip.outPoint.seconds + endingLength[0];
topNewSongClip.outPoint = time;


// 导入主榜
videoTime = makeRanks(contain, 0, videoTrack, imageTrack, mainVideoBin, mainImageBin, '主榜', videoTime, allData);
audioTime.ticks = videoTime.ticks;

// 导入副榜BGM
audioTime.seconds += 1;
var musicFiles = [currentFolder + 'BGM\\副榜.mp3'];
project.importFiles(musicFiles, false, musicBin, false);
var currentMusic = getByName(musicBin, "副榜.mp3");
var projectItemMetadata = currentMusic.getProjectColumnsMetadata();
projectItemMetadata = JSON.parse(projectItemMetadata);
var extendTime = projectItemMetadata[5]["ColumnValue"];
musicTrack.overwriteClip(currentMusic, audioTime.ticks);
var clip = musicTrack.clips[1];
audioTime.seconds += Number(extendTime) / ticks;
clip.end = audioTime;

// 导入副榜前图片
var endingImages = ["制作.png", "副榜.png"];
for (var i = 0; i < endingImages.length; i++) {
    project.importFiles([currentFolder + "其他图片\\" + endingImages[i]], false, otherImageBin, false);
}
var endingLength = [3, 3];
videoTime = importClips(otherImageBin, endingImages, endingLength, imageTrack, videoTime, 1);

// 导入副榜图片
var subImageFiles = [];
var lengths = [];
var extendSeconds = ((Number(extendTime) / ticks + 1) - sum(endingLength)) / 20;
for (var i = 0; i < (extend - contain) / 4; i++) {
    subImageFiles.push(currentFolder + '副榜图片\\' + (i + 1) + '.png');
    lengths.push(extendSeconds);
}
videoTime = importVideosToTrack(subImageFiles, subImageBin, imageTrack, lengths, videoTime, null);
project.save();

// 设置视频位置和缩放
var clips = videoTrack.clips;
for (var i = 0; i < clips.numItems; i++) {
    var clip = clips[i];
    videoSizeFit(clip, [1440, 810], [0.3875, 0.3965]);
}

// 音频关键帧处理
var clips = songTrack.clips;
for (var i = 0; i < clips.numItems; i++) {
    var clip = clips[i];
    audioFadeout(clip, 1);
}


