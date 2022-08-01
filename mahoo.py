from PIL import ImageSequence, ImageDraw, ImageFont
import re
import os
import json
import requests
from os import path
from io import BytesIO

from hoshino import Service, aiorequests
from hoshino.typing import CommandSession, CQEvent
import random
import textwrap
import opencc

from PIL import Image

sv_help = """
[召唤怪兽卡 + 名字 + 描述 + 图片] 生成怪兽卡
    PS: 如果选择图片时使用at，
    将会用对应用户的头像、昵称生成
[发动魔法卡 + 名字 + 描述 + 图片] 生成魔法卡
[发动陷阱卡 + 名字 + 描述 + 图片] 生成陷阱卡
"""

sv = Service(
    name='游戏王搓卡',
    visible=True,  # False隐藏
    enable_on_default=True,  # 是否默认启用
    bundle="娱乐"
)


@sv.on_fullmatch(["帮助游戏王", "帮助游戏王搓卡"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


async def save_img(image_url):
    image = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6) ",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "Accept-Language": "zh-cn"
               }
    try:
        if len(image_url) == 0:
            return None
        for url in image_url:
            response = await aiorequests.get(url, headers=headers)
            image.append(Image.open(BytesIO(await response.content)))
        return image
    except Exception as e:
        print(repr(e))
        return None


def get_all_img_url(event: CQEvent):
    all_url = []
    for i in event["message"]:
        if i["type"] == "image":
            all_url.append(i["data"]["url"])
    return all_url


def get_pic(qq):
    image = []
    api_path = f'https://q1.qlogo.cn/g?b=qq&nk={qq}&s=100'
    head = requests.get(api_path, timeout=20).content
    image.append(Image.open((BytesIO(head))))
    return image


def get_name(qq):
    url = 'https://r.qzone.qq.com/fcg-bin/cgi_get_portrait.fcg'
    params = {'uins': qq}
    res = requests.get(url, params=params)
    res.encoding = 'GBK'
    data_match = re.search(r'\{"%s":\[".+/%s/%s/.+]}' % (qq, qq, qq), res.text)
    if data_match:
        j_str = data_match.string
        j_str = j_str.split("portraitCallBack")[1].strip("(").strip(")")
        return json.loads(j_str)[qq][-2]
    else:
        return '神秘用户'


img = {}
send_times = {}
qq_name = None
is_get_msg = False


@sv.on_command('召唤怪兽卡', only_to_me=False)
async def summon_monster(session: CommandSession):
    global qq_name, is_get_msg
    event = session.ctx
    uid = event['user_id']
    if uid not in img:
        img[uid] = []
    if uid not in send_times:
        send_times[uid] = 0
    msg = event.message
    rule = re.compile(r"^\[CQ:image.+$")

    qq_head = None
    qq_rule = re.compile(r"^\[CQ:at,qq=\d+]")
    if re.match(qq_rule, event.raw_message):
        qq = re.findall(r"\d+", event.raw_message)
        qq_head = get_pic(qq[0])
        qq_name = get_name(qq[0])

    if re.match(rule, str(msg)) and len(img[uid]) == 0:
        image = await save_img(get_all_img_url(event))
        img[uid].extend(image)
    elif qq_head is not None and len(img[uid]) == 0:
        img[uid].extend(qq_head)
    elif len(img[uid]) == 1 and not re.match(rule, str(msg)) and qq_name is None:
        img[uid].extend(msg)
    elif len(img[uid]) == 1 and not re.match(rule, str(msg)) and qq_name is not None:
        msg = str(qq_name) + " " + msg
        img[uid].extend(msg)
        is_get_msg = True
    else:
        send_times[uid] += 1
    if send_times[uid] >= 3:
        img[uid] = []
        send_times[uid] = 0
        qq_name = None
        is_get_msg = False
        await session.finish('过多次未发送图片，已自动停止')

    if len(img[uid]) == 0:
        session.pause('请发送需要的卡片图片')
    elif len(img[uid]) == 1:
        session.pause('发送怪兽卡名字及信息')
    elif len(img[uid]) >= 2:
        bg = img[uid][0]
        kw = img[uid][1].data["text"]
        pic = gif_card(bg, 1, kw)
        msg = f'[CQ:image,file=file:///{pic}]'
        img[uid] = []
        send_times[uid] = 0
        qq_name = None
        is_get_msg = False
        await session.finish(msg)


@sv.on_prefix('发动魔法卡', only_to_me=False)
async def summon_magic(session: CommandSession):
    global qq_name, is_get_msg
    event = session.ctx
    uid = event['user_id']
    if uid not in img:
        img[uid] = []
    if uid not in send_times:
        send_times[uid] = 0
    msg = event.message
    rule = re.compile(r"^\[CQ:image.+$")

    qq_head = None
    qq_rule = re.compile(r"^\[CQ:at,qq=\d+]")
    if re.match(qq_rule, event.raw_message):
        qq = re.findall(r"\d+", event.raw_message)
        qq_head = get_pic(qq[0])
        qq_name = get_name(qq[0])

    if re.match(rule, str(msg)) and len(img[uid]) == 0:
        image = await save_img(get_all_img_url(event))
        img[uid].extend(image)
    elif qq_head is not None and len(img[uid]) == 0:
        img[uid].extend(qq_head)
    elif len(img[uid]) == 1 and not re.match(rule, str(msg)) and qq_name is None:
        img[uid].extend(msg)
    elif len(img[uid]) == 1 and not re.match(rule, str(msg)) and qq_name is not None:
        msg = str(qq_name) + " " + msg
        img[uid].extend(msg)
        is_get_msg = True
    else:
        send_times[uid] += 1
    if send_times[uid] >= 3:
        img[uid] = []
        send_times[uid] = 0
        qq_name = None
        is_get_msg = False
        await session.finish('过多次未发送图片，已自动停止')

    if len(img[uid]) == 0:
        session.pause('请发送需要的卡片图片')
    elif len(img[uid]) == 1:
        session.pause('发送魔法卡名字及信息')
    elif len(img[uid]) >= 2:
        bg = img[uid][0]
        kw = img[uid][1].data["text"]
        pic = gif_card(bg, 1, kw)
        msg = f'[CQ:image,file=file:///{pic}]'
        img[uid] = []
        send_times[uid] = 0
        qq_name = None
        is_get_msg = False
        await session.finish(msg)


@sv.on_prefix('发动陷阱卡', only_to_me=False)
async def summon_trap(session: CommandSession):
    global qq_name, is_get_msg
    event = session.ctx
    uid = event['user_id']
    if uid not in img:
        img[uid] = []
    if uid not in send_times:
        send_times[uid] = 0
    msg = event.message
    rule = re.compile(r"^\[CQ:image.+$")

    qq_head = None
    qq_rule = re.compile(r"^\[CQ:at,qq=\d+]")
    if re.match(qq_rule, event.raw_message):
        qq = re.findall(r"\d+", event.raw_message)
        qq_head = get_pic(qq[0])
        qq_name = get_name(qq[0])

    if re.match(rule, str(msg)) and len(img[uid]) == 0:
        image = await save_img(get_all_img_url(event))
        img[uid].extend(image)
    elif qq_head is not None and len(img[uid]) == 0:
        img[uid].extend(qq_head)
    elif len(img[uid]) == 1 and not re.match(rule, str(msg)) and qq_name is None:
        img[uid].extend(msg)
    elif len(img[uid]) == 1 and not re.match(rule, str(msg)) and qq_name is not None:
        msg = str(qq_name) + " " + msg
        img[uid].extend(msg)
        is_get_msg = True
    else:
        send_times[uid] += 1
    if send_times[uid] >= 3:
        img[uid] = []
        send_times[uid] = 0
        qq_name = None
        is_get_msg = False
        await session.finish('过多次未发送图片，已自动停止')

    if len(img[uid]) == 0:
        session.pause('请发送需要的卡片图片')
    elif len(img[uid]) == 1:
        session.pause('发送陷阱卡名字及信息')
    elif len(img[uid]) >= 2:
        bg = img[uid][0]
        kw = img[uid][1].data["text"]
        pic = gif_card(bg, 1, kw)
        msg = f'[CQ:image,file=file:///{pic}]'
        img[uid] = []
        send_times[uid] = 0
        qq_name = None
        is_get_msg = False
        await session.finish(msg)


def gif_card(card_img, num, kw):
    arr = kw.split(' ')
    cc = opencc.OpenCC('s2t')
    word1 = cc.convert(f'{arr[0]}')
    word2 = cc.convert(f'{arr[1]}')
    gif_path = path.join(path.dirname(__file__), 'out')
    type_name = "怪兽卡"
    bg_path = path.join(path.dirname(__file__), './img/png (怪兽).jpg')
    if num == 1:  # '怪兽':
        type_name = "怪兽卡"
        bg_path = path.join(path.dirname(__file__), './img/png (怪兽).jpg')
    elif num == 2:  # '魔法':
        type_name = "魔法卡"
        bg_path = path.join(path.dirname(__file__), './img/png (魔法).jpg')
    elif num == 3:  # '陷阱':
        type_name = "陷阱卡"
        bg_path = path.join(path.dirname(__file__), './img/png (陷阱).jpg')
    card_name1 = f'{type_name}_{word1}.gif'
    card_name2 = f'{type_name}_{word1}.jpg'
    out_path = path.join(gif_path, card_name1)
    out_path2 = path.join(gif_path, card_name2)
    if len(word2) >= 138:
        word2 = word2[0:138]
    new_frames = []
    gif = card_img
    bg = Image.open(bg_path)
    draw = ImageDraw.Draw(bg)
    font1 = ImageFont.truetype(os.path.join(os.path.dirname(__file__), '华康隶书体W3.TTC'), 20)
    font2 = ImageFont.truetype(os.path.join(os.path.dirname(__file__), '华康隶书体W3.TTC'), 14)
    draw.text((27, 24), word1, fill=(0, 0, 0), font=font1)
    # draw.text((27, 319), word2, fill=(0 , 0, 0), font=font2)
    if num == 1:  # '怪兽':
        font3 = ImageFont.truetype(os.path.join(os.path.dirname(__file__), '华康隶书体W3.TTC'), 14)
        mom_atk = f'{int(random.uniform(1, 100)) * 100}'
        mom_def = f'{int(random.uniform(1, 100)) * 100}'
        draw.text((179, 380), mom_atk, fill=(0, 0, 0), font=font3)
        draw.text((238, 380), mom_def, fill=(0, 0, 0), font=font3)
    para = textwrap.wrap(word2, width=16)
    current_h, pad = 319, 0
    for line in para:
        w, h = draw.textsize(line, font=font2)
        draw.text((27, current_h), line, fill=(0, 0, 0), font=font2)
        current_h += h + pad
    try:
        gif.seek(1)
    except EOFError:
        isanimated = False
    else:
        isanimated = True
    if isanimated:
        top_bgwidth = 219
        top_width = 219
        for frame in ImageSequence.Iterator(gif):
            new_bg = bg.copy()
            frame = frame.convert('RGB')
            new_bg.paste(frame.resize((top_width, top_bgwidth)),
                         (34, 77))
            new_frames.append(new_bg)

        new_frames[0].save(out_path, save_all=True,
                           append_images=new_frames, optimize=False, duration=24, loop=0)
        return path.abspath(out_path)
    else:
        new_bg = bg.copy()
        frame = gif.copy()
        top_bgwidth = 219
        top_width = 219
        new_bg.paste(frame.resize((top_width, top_bgwidth)),
                     (34, 77))
        new_bg.save(out_path2)
        return path.abspath(out_path2)
