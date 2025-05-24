#include 'pr.jsx'

var MODE = 'weekly';

if (MODE == 'daily' || MODE == 'weekly') {
    var contain = 20;
    var extend = 100;
    var news = 10;
}else if (MODE == 'monthly') {
    var contain = 20;
    var extend = 200;
    var news = 20;
}

var metadata = readJSONFile(currentFolder + '基本信息数据.json');

var sequenceName = "排行榜";
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
if (MODE === 'daily'){

    var openingImages = ["16比9封面.png", "OP.png", "日刊\\公式.png", "日刊\\榜单.png", "新曲榜.png"];
    var openingLength = [3, 5, 5, 5, 3];
} else if (MODE === 'weekly') {

    var openingImages = ["16比9封面.png", "OP.png",  "规则1.png", "规则2.png", "规则3.png", "周刊\\公式.png", "周刊\\成就.png", "周刊\\榜单.png", "新曲榜.png"];
    var openingLength = [3, 5, 5, 5, 5, 5, 5, 5, 3];
} else if (MODE === 'monthly') {

    var openingImages = ["月刊\\封面.png", "OP.png", "规则1.png", "规则2.png", "规则3.png",  "月刊\\公式.png", "月刊\\榜单.png", "月刊\\新曲榜.png"];
    var openingLength = [3, 5, 5, 5, 5, 5, 5, 3];
}


for (var i = 0; i < openingImages.length; i++) {
    $.writeln(i);
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

// 导入副榜和前后图片
if (MODE == 'daily'){
    var subImages = [currentFolder + "其他图片\\" + "统计数据.png",currentFolder + "其他图片\\" +  "统计2.png",currentFolder + "其他图片\\" +  "制作.png",currentFolder + "其他图片\\" +  "副榜.png"];
    var subLengths = [5, 5, 3, 3];
}else if (MODE == 'weekly'){
    var subImages = [currentFolder + "其他图片\\" + "统计歌手.png",currentFolder + "其他图片\\" +  "统计数据.png"];
    var subLengths = [12, 5];
    var millionStats = readJSONFile(currentFolder + "百万达成.json");
    for(var i=0;i<millionStats.length;i++){
        if (i%5 == 0){
            subImages.push(currentFolder + "其他图片\\百万达成" + (i/5+1) + ".png");
            subLengths.push(6);
        }
    }
    var achievementStats = readJSONFile(currentFolder + "成就.json");
    for(var i=0;i<achievementStats.length;i++){
        if (i%5 == 0){
            subImages.push(currentFolder + "其他图片\\成就达成" + (i/5+1) + ".png");
            subLengths.push(6);
        }
    }
    subImages.push(currentFolder + "其他图片\\" +  "制作.png",currentFolder + "其他图片\\" +  "副榜.png");
    subLengths.push(8,3);

}else if (MODE == 'monthly'){
    var subImages = [currentFolder + "其他图片\\" + "统计歌手.png",currentFolder + "其他图片\\" +  "统计数据.png",currentFolder + "其他图片\\" +  "制作.png",currentFolder + "其他图片\\" +  "副榜.png"];
    var subLengths = [12, 5, 8, 3];
}
var extendSeconds = ((Number(extendTime) / ticks + 1) - sum(subLengths) - 3) / (extend - contain) * 4;
for (var i = 0; i < (extend - contain) / 4; i++) {
    subImages.push(currentFolder + '副榜图片\\' + (i + 1) + '.png');
    subLengths.push(extendSeconds);
}

subImages.push(currentFolder + '其他图片\\结尾1.png' );
subLengths.push(3);

project.importFiles(subImages, false, subImageBin, false);



videoTime = importClips(subImageBin, subImages, subLengths, imageTrack, videoTime, 1);
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

