#include 'pr.jsx'

var sequenceName = "大日刊";
var project = app.project;
var sequence = project.sequences[0];
var videoTracks = sequence.videoTracks;
var videoTrack = videoTracks[1];

// 设置视频位置和缩放
var clips = videoTrack.clips;
for (var i = 0; i < clips.numItems; i++) {
    var clip = clips[i];
    videoSizeFit(clip, [1347.8, 758.2], [0.3802, 0.3991]);
}
// 音频关键帧处理
var clips = songTrack.clips;
for (var i = 0; i < clips.numItems; i++) {
    var clip = clips[i];
    audioFadeout(clip, 1);
}