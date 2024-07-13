## app的结构
* project
  * rootItem
    * children -> projectItem
  * sequence
    * videoTracks/audioTracks -> track
      * clips -> trackItem
        * component -> component
          * properties -> componentParam

## 效果控件设置方法

一部分参数可以开启关键帧，一部分不能。`.areKeyframesSupported()`查询是否支持关键帧。

对于可以开启关键帧的参数，`.isTimeVarying()`获取当前是否启用关键帧，`.setTimeVarying(true)`开启关键帧。

### 不使用关键帧控制参数

参数是数字或者数组。`.getValue()`获取参数。`.setValue()`设置参数。

### 使用关键帧控制参数

注意，使用的时间都是在原视频素材中的时间，也就是说需要加上inPoint。

`.getKeys()`获取所有关键帧，返回包含时间对象的序列。

`.addKey(time)`在指定时间点添加关键帧。

`.setValueAtKey(time, value)`设置关键帧的值。

## Time对象

1 second == 254016000000 ticks

`time.seconds`是数字类型，`time.ticks`是字符串类型。

`Time()`无法接收任何参数。

## 效果控件内容

### 一般视频

1. Opacity
2. Motion
    1. 位置 [Array]
    2. 缩放
    3. 缩放宽度
    4. 等比缩放
    5. 旋转
    6. 锚点
    7. 防闪烁滤镜

### 一般音频

1. Internal Volume Stereo
    1. （旁路）
    2. 级别
2. Internal Channel Volume Stereo

## 诸多入点出点的区别

### projectItem.getInPoint() / projectItem.getOutPoint()

这是原视频的入点出点。也就是通过源监视器手动打的入点出点。

`.getInPoint()`返回`time`对象，`.setOutPoint()`使用`ticks`。

### trackItem.inPoint / trackItem.outPoint

这是时间轴当中`clip`的内置入点和出点，关系到效果控件中的关键帧。这个时间流速正常，但是时间点和其他时间不同，具体怎么回事我还不清楚。

两个都是时间对象，且可以直接读写。但是注意不要直接用`trackItem.outPoint.seconds += 3;`这样的方法，应该用新的时间对象来赋值。

### trackItem.start / trackItem.end

这是`clip`在时间轴上的开始和结束时间。关键帧的设置可以在这个范围之外。

两个都是时间对象，同上。