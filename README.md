# genshin-lyre-auto-play-without-midi

## 无需MIDI文件的原神风物之诗琴自动演奏程序

使用普通的文本文件作为谱子（存放在 `spectrums` 文件夹中），谱子内写键盘按键或手机谱（即简谱符号）

[演示视频1](https://www.bilibili.com/video/BV1C3411C7n6/) | [演示视频2](https://www.bilibili.com/video/BV1dT4y1o7dY/) | [演示视频3](https://www.bilibili.com/video/BV1Bq4y157Ke/)

目前暂不提供可执行文件（人话：直接打开就能用的程序），但是可自己配置环境运行

注意：因为没有使用 MIDI 文件，所以每个音符的间隔和时长都是固定的，因此不太完美比较生硬，不及真人弹奏和 MIDI

> P.S. 风物之诗琴本身也没有延音和半高音，音域也比较窄，有很多歌曲都要修改才能用，挺遗憾的

### 原理

模拟按键，仅此而已，非常简单

### 使用方法

1. 使用 Git clone 本仓库或直接下载本仓库的[压缩包](https://github.com/Redlnn/genshin-lyre-auto-play-without-midi/archive/refs/heads/master.zip)并解压到一个文件夹内
2. 配置运行环境

   1. 一台 Windows 设备  
   2. 安装 Python，版本 >= 3.10  
   3. 双击打开 `安装依赖.bat` 安装所需的依赖库

3. 使用 __文本编辑器__（如记事本）打开 `config.py`，修改要读取的谱子的文件名（__请不要碰任何的引号__）和 BPM 并保存

   > BPM 即 节拍数每分钟，即每分钟多少个节拍（多少个音符）

4. 直接双击 `开始演奏.bat` 开始运行（运行前需确认 Python 环境配置好了）

### 如何添加新谱子

你可以自行添加新谱子，但对于网上别人的谱子需要进行一定的修改才可以使用

支持写键盘按键和具体的音符（即所谓的手机谱，如 `+1 2 -3`），不支持读 MIDI 文件

为了方便程序识别，对于谱子文件内容的格式存在一些硬性规范

格式规范如下（看不懂的话可参考自带的几首谱子）：

1. 若谱子内含有非英文与数字的字符或符号（如在注释中写中文），请使用 `UTF-8`（无BOM）编码保存，不要使用 `ANSI`、`GBK`、`GB2312` 或 `GB18030` 等编码保存
2. 谱子内每一个音符均使用空格分开，不能连续两个音符

   > 如 `A S 0 D F`，不能这样写 `AS DF`  
   > 或 `1 +2 3 -4`，不能这样写 `1+2 -34`

3. 程序是等时间间模拟隔逐个按下键盘按键（一个按键即一个音符），因此如果想要停顿（即不按下任何按键），请类似简谱一样使用 0 占位（如上面一行所示），所以也可以把谱子理解为没有区分音符长度及没有分小节的简谱
4. 如果要同时按下多个按键，请使用半角英文括号括住要按下的按键，并且中间不能含有空格

   > 如 `A (SD) 0 (FGH)`  
   > 或 `1 (+23) 0 (4-56+7)`

5. 如果有在播放时动态改变 BPM 的需求，可使用 `#` 后跟 BPM 数值，`#` 与数字间不可以有空格，可放在任意位置

   > 如 `A #180 D S #210 (FGH) J Q`  
   > 当然也可以把 `#180` 或 `#210` 放在单独的一行，若与其他元素（如音符或注释）处于同一行，请确保其前后均有空格

6. 如果有需要写注释的需求，比如标记段落标题，请使用两条斜杠 `//` 后接注释内容（如：`//我是注释`），使用方法与位置类似改变 BPM 的 `#180` 相同

### 一些声明

1. 本程序运行过程中需要获取管理员权限是因为原神具有反作弊保护，没有管理员权限无法在游戏中模拟按键
2. 自带的几首谱子均非原创而是来自B站的视频，并经过了一定的修改，具体原视频及原作者请在谱子文件中查看
3. 此程序不保证不会被米哈游认为是作弊行为，使用本程序仍然有可能会有所谓封号的风险，使用本程序代表你已知晓该风险
4. 本程序不含有对原神游戏数据及用户系统文件和设置进行修改的行为，但请确保来源安全


### 不足之处

1. 程序运行时，每个音符间隔的时间会受到计算机性能的影响而不稳定
2. 日志输出没有独立，会影响主线程的运行，会导致每个音符间隔的时间不稳定
3. 没有做连音的处理（咕咕咕）
4. 不会写好康的 GUI（~~理直气壮！~~）
5. 没写判断是否已进入/退出弹琴界面，退出了弹琴界面会变得好像乱按一通
