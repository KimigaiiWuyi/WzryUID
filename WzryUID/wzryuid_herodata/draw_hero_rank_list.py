from pathlib import Path
from datetime import datetime
from typing import Dict, List, Union

from PIL import Image, ImageDraw
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.fonts.fonts import core_font as cf
from gsuid_core.utils.image.image_tools import crop_center_img

from ..utils.wzry_api import wzry_api
from ..utils.error_reply import get_error
from ..utils.download import download_file
from ..utils.resource_path import TEMP_PATH, AVATAR_PATH

TEXT_PATH = Path(__file__).parent / 'texture2d'

COLOR = [
    (233, 63, 63),
    (155, 63, 233),
    (63, 141, 233),
    (113, 178, 97),
    (263, 139, 68),
]

HERO_COLOR = {
    '战士': (182, 84, 25),
    '射手': (225, 51, 117),
    '法师': (51, 93, 225),
    '坦克': (113, 102, 43),
    '刺客': (175, 51, 225),
    '辅助': (69, 136, 25),
}

POS_COLOR = {
    0: HERO_COLOR['战士'],
    1: HERO_COLOR['法师'],
    2: HERO_COLOR['射手'],
    3: HERO_COLOR['辅助'],
    4: HERO_COLOR['刺客'],
}

SEG_MODE = {
    '所有段位': 1,
    '巅峰1350+': 3,
    '顶端排位': 4,
    '赛事选择': 5,
}


async def draw_hero_rank_pic(mode: str = '所有段位'):
    mode = mode.replace('尖端', '顶端').replace('头部', '顶端')
    _mode = mode
    for sindex, sm in enumerate(SEG_MODE):
        if mode in sm:
            seg = SEG_MODE[sm]
            title_color = COLOR[sindex]
            _mode = sm
            break
    else:
        title_color = COLOR[0]
        _mode = '所有段位'
        seg = 1

    cache_path = TEMP_PATH / f'英雄榜-{mode}.jpg'
    if cache_path.exists():
        return await convert_img(cache_path)

    result: Dict[str, Dict[int, List[List[Union[str, int]]]]] = {}

    for g in range(1, 6):
        _data = await wzry_api.get_hero_rank_list(seg, g)
        if isinstance(_data, int):
            return get_error(_data)
        data = _data['resultList']
        for tier in data:
            hero_list = tier['list']
            tier_label = tier['label']
            if tier_label not in result:
                result[tier_label] = {}
            if g not in result[tier_label]:
                result[tier_label][g] = []
            for hero in hero_list:
                hero_id = hero['heroId']
                hero_name = hero['heroName']
                hero_career = hero['heroCareer']

                result[tier_label][g].append(
                    [
                        hero_id,
                        hero_name,
                        hero_career,
                    ]
                )

                hero_path = AVATAR_PATH / f'{hero_id}.png'
                if not hero_path.exists():
                    await download_file(
                        hero['heroIcon'],
                        AVATAR_PATH,
                        f'{hero_id}.png',
                    )

    w, h = 3500, 600
    tier_h_lst = []
    for t in result:
        # T0
        pos = result[t]
        max_len = max([len(x) for x in list(pos.values())])
        th = (((max_len - 1) // 3) + 1) * 150
        tier_h_lst.append(th)
        h += th + 100

    h += 50

    img = crop_center_img(Image.open(TEXT_PATH / 'bg.jpg'), w, h)

    title = Image.new('RGBA', (3500, 350))
    title_draw = ImageDraw.Draw(title)
    title_draw.rectangle((78, 84, 3422, 236), title_color)
    title_draw.rounded_rectangle((1412, 268, 2088, 320), 60, title_color)
    title_draw.rounded_rectangle((2190, 122, 2458, 198), 60, 'White')

    title_word = Image.open(TEXT_PATH / 'title.png')
    title.paste(title_word, (0, 0), title_word)

    current_time = datetime.now()
    update_time = current_time.strftime("%Y.%m.%d %H:%M:%S")

    title_draw.text(
        (1750, 294),
        f'最后更新时间: {update_time}',
        'White',
        cf(38),
        'mm',
    )
    title_draw.text(
        (2324, 160),
        _mode,
        title_color,
        cf(46),
        'mm',
    )

    img.paste(title, (0, 0), title)

    img_draw = ImageDraw.Draw(img)

    _th = 590
    for tindex, th in enumerate(tier_h_lst):
        old_th = _th
        new_th = old_th + th
        tx, ty = 165, old_th + 60
        img_draw.rectangle((310, old_th, 325, new_th), COLOR[tindex])

        img_draw.rectangle(
            (tx - 80, ty - 60, tx + 150, ty + 60), COLOR[tindex]
        )
        img_draw.text((tx, ty), f'T{tindex}', 'White', cf(65), 'lm')

        _th += 100 + th

    for ppindex, pp in enumerate(['对抗路', '中路', '发育', '游走', '打野']):
        xx, yy = 625 + 575 * ppindex, 430
        of1, of2 = 143, 46
        img_draw.rounded_rectangle(
            (xx - of1, yy - of2, xx + of1, yy + of2), 0, POS_COLOR[ppindex]
        )
        img_draw.text(
            (xx, yy),
            pp,
            'White',
            cf(80),
            'mm',
        )

    hero_fg = Image.open(TEXT_PATH / 'hero_fg.png')
    for tindex, t in enumerate(result):
        pos = result[t]
        for p in pos:
            hero_list = pos[p]

            _x = 400 + (p - 1) * 576
            _y = 590 + sum(tier_h_lst[:tindex]) + tindex * 100

            for hindex, hero_d in enumerate(hero_list):
                hero_id, hero_name, careers = hero_d[0], hero_d[1], hero_d[2]
                hero_path = AVATAR_PATH / f'{hero_id}.png'
                avatar = Image.open(hero_path).convert('RGBA')
                avatar = avatar.resize((140, 140))

                assert isinstance(careers, str)
                career_lst = careers.split('/')

                if len(career_lst) == 1:
                    hero_color = HERO_COLOR[career_lst[0]]
                    hero_fgc = Image.new('RGBA', avatar.size, hero_color)
                else:
                    hero_fgc = Image.new('RGBA', avatar.size)
                    hero_fgc_draw = ImageDraw.Draw(hero_fgc)
                    hero_fgc_draw.rectangle(
                        (0, 0, 70, 140),
                        fill=HERO_COLOR[career_lst[0]],
                    )
                    hero_fgc_draw.rectangle(
                        (70, 0, 140, 140),
                        fill=HERO_COLOR[career_lst[1]],
                    )

                avatar.paste(hero_fgc, (0, 0), hero_fg)
                avatar_draw = ImageDraw.Draw(avatar)

                avatar_draw.text(
                    (72, 124),
                    f'{hero_name}',
                    'White',
                    cf(26),
                    'mm',
                )

                x = _x + (hindex % 3) * 150
                y = _y + (hindex // 3) * 150
                img.paste(avatar, (x, y), avatar)

    footer = Image.open(TEXT_PATH / 'footer.png')
    img.paste(footer, (0, h - 100), footer)

    img.save(cache_path, 'JPEG', quality=89, optimize=True)

    return await convert_img(img)
