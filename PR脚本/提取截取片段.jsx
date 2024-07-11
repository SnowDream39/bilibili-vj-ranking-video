#include "json2.js"
#include "pr.jsx"


var project = app.project;
var rootItem = project.rootItem;
var videoBin = getByName(rootItem, "截取片段用视频");

var clipPoints = readJSONFile(currentFolder + '截取片段.json');

var videoClips = videoBin.children;
$.writeln(videoClips);

for (var i = 0; i < videoClips.numItems; i++) {
    var videoClip = videoClips[i];
    var bvid = videoClip.name.substring(0, 12);
    var inPoint = videoClip.getInPoint().ticks;
    var outPoint = videoClip.getOutPoint().ticks;
    var found = false;
    for (var j = 0; j < clipPoints.length; j++) {
        if (bvid === clipPoints[j].bvid) {
            clipPoints[j].inPoint = inPoint;
            clipPoints[j].outPoint = outPoint;
            found = true;
        }
    }
    if (!found) {
        clipPoints.push({
            'bvid': bvid,
            'inPoint': inPoint,
            'outPoint': outPoint
        });
    }
}
writeJSONFile(currentFolder + '截取片段.json', clipPoints);

var dataToday = readJSONFile(currentFolder + '数据.json');
for (var i=0; i<dataToday.length;i++){
    var bvid = dataToday[i]['bvid']
    if (jsonGet(clipPoints, 'bvid', bvid)) {
        dataToday[i]['inPoint'] = jsonGet(clipPoints, 'bvid', bvid).inPoint;
        dataToday[i]['outPoint'] = jsonGet(clipPoints, 'bvid', bvid).outPoint; 
    }

}

writeJSONFile(currentFolder + '数据.json',dataToday)

var dataTodayNew = readJSONFile(currentFolder + '新曲数据.json');
for (var i=0; i<dataTodayNew.length;i++){
    var bvid = dataTodayNew[i]['bvid']
    if (jsonGet(clipPoints, 'bvid', bvid)) {
        dataTodayNew[i]['inPoint'] = jsonGet(clipPoints, 'bvid', bvid).inPoint;
        dataTodayNew[i]['outPoint'] = jsonGet(clipPoints, 'bvid', bvid).outPoint; 
    }
}

writeJSONFile(currentFolder + '新曲数据.json',dataTodayNew)

