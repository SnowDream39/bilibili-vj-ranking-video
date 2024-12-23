#include 'pr.jsx'

var rootItem = app.project.rootItem;
var cutBin = refreshBin(rootItem, "截取片段用视频");

var bvids = readJSONFile(currentFolder + "缺少截取片段视频.json");
var videoFiles = [];
for (var i=0; i<bvids.length; i++) {
    videoFiles.push(currentFolder + "视频//" + bvids[i] + ".mp4");
}

app.project.importFiles(videoFiles,false, cutBin,false);