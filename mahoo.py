from PIL import Image, ImageSequence,ImageDraw, ImageFont
import requests
import re
import os
from os import path
from io import BytesIO
from hoshino import Service, aiorequests
import random
import textwrap
import opencc

sv = Service('mahoo')

@sv.on_prefix(('召唤怪兽卡'), only_to_me=False)
async def text_add(bot, ev):
    kw = ev.message.extract_plain_text().strip()
    match = re.search(r"\[CQ:image,file=(.*),url=(.*)\]", str(ev.message))
    if not match:
        await bot.send(ev,f'图片呢？', at_sender=True)
        return
    resp = await aiorequests.get(match.group(2))
    resp_cont = await resp.content
    print(kw)
    pic = gif_card(BytesIO(resp_cont), 1,kw)
    await bot.send(ev,f'[CQ:image,file=file:///{pic}]')
    
@sv.on_prefix(('发动魔法卡'), only_to_me=False)
async def text_add(bot, ev):
    kw = ev.message.extract_plain_text().strip()
    match = re.search(r"\[CQ:image,file=(.*),url=(.*)\]", str(ev.message))
    if not match:
        await bot.send(ev,f'图片呢？', at_sender=True)
        return
    resp = await aiorequests.get(match.group(2))
    resp_cont = await resp.content
    pic = gif_card(BytesIO(resp_cont), 2,kw)
    await bot.send(ev,f'[CQ:image,file=file:///{pic}]')    
    
@sv.on_prefix(('发动陷阱卡'), only_to_me=False)
async def text_add(bot, ev):
    kw = ev.message.extract_plain_text().strip()
    match = re.search(r"\[CQ:image,file=(.*),url=(.*)\]", str(ev.message))
    if not match:
        await bot.send(ev,f'图片呢？', at_sender=True)
        return
    resp = await aiorequests.get(match.group(2))
    resp_cont = await resp.content
    pic = gif_card(BytesIO(resp_cont), 3, kw)
    await bot.send(ev,f'[CQ:image,file=file:///{pic}]')    

def gif_card(gifpath, num, kw):
    arr = kw.split(' ')
    cc = opencc.OpenCC('s2t')
    word1 = cc.convert(f'{arr[0]}')
    word2 = cc.convert(f'{arr[1]}') 
    GIF_PATH = path.join(path.dirname(__file__),'out')
    if num == 1: #'怪兽':
        type_name = "怪兽卡"
        atk = f'{random.randint(1,10)*100}'
        bgPath = path.join(path.dirname(__file__), './img/png (怪兽).jpg')
    elif num == 2: #'魔法':
        type_name = "魔法卡"
        bgPath = path.join(path.dirname(__file__), './img/png (魔法).jpg')
    elif num == 3: #'陷阱':
        type_name = "陷阱卡"
        bgPath = path.join(path.dirname(__file__), './img/png (陷阱).jpg')
    card_name1 = f'{type_name}_{word1}.gif'
    card_name2 = f'{type_name}_{word1}.jpg'
    outPath = path.join(GIF_PATH,card_name1)
    outPath2 = path.join(GIF_PATH,card_name2) 
    if len(word2) >= 138:
        word2 = word2[0:138]
    newFrames = []
    gif = Image.open(gifpath)
    bg = Image.open(bgPath)
    draw = ImageDraw.Draw(bg)
    font1 = ImageFont.truetype(os.path.join(os.path.dirname(__file__),'华康隶书体W3.TTC'), 20)
    font2 = ImageFont.truetype(os.path.join(os.path.dirname(__file__),'华康隶书体W3.TTC'), 14)
    draw.text((27, 24), word1, fill=(0, 0, 0), font=font1)    
    #draw.text((27, 319), word2, fill=(0 , 0, 0), font=font2)
    if num == 1: #'怪兽':
        font3 = ImageFont.truetype(os.path.join(os.path.dirname(__file__),'华康隶书体W3.TTC'), 14)
        mom_atk = f'{int(random.uniform(1,100))*100}'
        mom_def = f'{int(random.uniform(1,100))*100}'
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
    if(isanimated):
        topBgwidth = 219
        topWidth = 219
        for frame in ImageSequence.Iterator(gif):
            newBg = bg.copy()
            frame = frame.convert('RGB')
            newBg.paste(frame.resize((topWidth, topBgwidth)),
                    (34, 77))
            newFrames.append(newBg)
        
        newFrames[0].save(outPath, save_all=True,
                          append_images=newFrames, optimize=False, duration=24, loop=0)
        return path.abspath(outPath)
    else:
        newBg = bg.copy()
        frame = gif.copy()
        topBgwidth = 219
        topWidth = 219
        newBg.paste(frame.resize((topWidth, topBgwidth)),
                    (34, 77))
        newBg.save(outPath2)
        return path.abspath(outPath2)







