#语音转换

##字符串转语音
接口地址: http://Android Http server addr/media/convert

方法: POST

参数:
```
{
  "action":"convert",
  "volume":5,
  "speed":5,
  "pitch":5,
  "speaker" : 0,   #0 :普通女声   1:普通男声
  "fileList" : [
    {"id":C001,"text":"请张三到第一诊室就诊"},
    {"id":C002,"text":"请李四到第一诊室就诊"},
    {"id":C003,"text":"请王武到第一诊室就诊"},
  ]
}
```
返回内容:
```
{ 
  "rescode": "200"
  "errInfo": "success",
  "fileformate": "wav",
  "fileList" : [
    {"id":C001,"path":"192.168.17.122/media/C001.wav"},
    {"id":C002,"path":"192.168.17.122/media/C002.wav"},
    {"id":C003,"path":"192.168.17.122/media/C002.wav"},
  ]
}```
