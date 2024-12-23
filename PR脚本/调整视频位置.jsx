#include 'pr.jsx'

var sequenceName = "排行榜";
var project = app.project;
var sequence = project.sequences[0];
var videoTracks = sequence.videoTracks;
var videoTrack = videoTracks[1];

// 设置视频位置和缩放
var clips = videoTrack.clips;
for (var i = 0; i < clips.numItems; i++) {
    var clip = clips[i];
    videoSizeFit(clip, [1449.1, 815.1], [0.3885, 0.3943]);
}