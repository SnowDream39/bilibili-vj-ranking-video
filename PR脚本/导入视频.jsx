#include 'pr.jsx'

var sequenceName = "特刊";
var project = app.project;
var rootItem = project.rootItem;

var sequences = project.sequences;
for (var i = 0; i < sequences.length; i++) {
    project.deleteSequence(sequences[i]);
}
var sequence = project.createNewSequence(sequenceName, "standard");

var audioTracks = sequence.audioTracks;
var musicTrack = audioTracks[0];
var songTrack = audioTracks[1];
var videoTracks = sequence.videoTracks;
var imageTrack = videoTracks[0];
var videoTrack = videoTracks[1];

var cutBin = refreshBin(rootItem, '截取片段用视频');
var monthReviewImageBin = refreshBin(rootItem, '月回顾图片');
var monthReviewVideoBin = refreshBin(rootItem, '月回顾视频');

data = readJSONFile(currentFolder + "视频列表.json")
points = readJSONFile(currentFolder + "截取片段.json")

var lengths = [];
var imageFiles = [];
var videoFiles = [];


for (var i = 0; i < data.length; i++) {
    var bvid = data[i].bvid;
    filepath = currentFolder + "视频\\" + bvid + ".mp4";
    if (videoFiles.indexOf(filepath) === -1){
        videoFiles.push(filepath);
    }
}
project.importFiles(videoFiles,false, monthReviewVideoBin,false)


var videoItems = monthReviewVideoBin.children;
for(var i=0; i<videoItems.length; i++){
    var item = videoItems[i];
    bvid = item.name.split('.')[0];
    item.setInPoint(jsonGet(points, 'bvid', bvid).inPoint,4);
    item.setOutPoint(jsonGet(points, 'bvid', bvid).outPoint,4);
    item.name = jsonGet(data, 'bvid', bvid).belongs + jsonGet(data, 'bvid', bvid).rank

}


project.save();

