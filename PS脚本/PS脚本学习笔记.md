## app的结构

* documents -> document (activeDocument)
    * layers -> layer
        * textItem
            * contents 
            * horizontalScale
            * verticalScale


## 图层的坐标

`layer.bounds`获取左上右下四个坐标。

`layer.translate(deltaX, deltaY)`相对移动。

没有绝对移动方法。可以首先`newLayer.translate(-layer.bounds[0], -layer.bounds[1])`移动到原点位置。