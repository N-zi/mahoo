# mahoo
HoshinoBot娱乐插件，在群内生成游戏王卡图

#安装
到`/hoshino/modules`目录下`git clone`   
并在 `/hoshino/config/__bot__.py`的`MODULES_ON`处添加`mahoo`开启模块

#指令
-
|  指令   | 说明  |
|  ----  | ----  |
| 召唤怪兽卡`卡名` `卡片描述``图片` |生成对应描述怪兽卡 |
| 发动魔法卡`卡名` `卡片描述``图片` |生成对应描述魔法卡 |
| 发动陷阱卡`卡名` `卡片描述``图片` |生成对应描述陷阱卡 |

#tips：
图片支持gif，gif太大或帧数太多酌情考虑服务器配置
生成的图片会存在`/hoshino/modules/mahoo/out` 目录下
文字部分使用繁体，简体部分不显示
