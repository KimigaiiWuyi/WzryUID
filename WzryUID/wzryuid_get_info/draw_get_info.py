from io import BytesIO
from pathlib import Path
from typing import Tuple, Union, Optional

import httpx
from PIL import Image, ImageDraw, ImageFilter
from gsuid_core.utils.fonts.fonts import core_font
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import (
    get_pic,
    get_color_bg,
    get_qq_avatar,
    draw_pic_with_ring,
)

from ..utils.wzry_api import wzry_api
from ..utils.error_reply import get_error
from ..utils.download import download_file
from ..utils.resource_path import BG_PATH, ICON_PATH

TEXT_PATH = Path(__file__).parent / 'texture2d'


async def draw_info_img(user_id: str, yd_user_id: str) -> Union[str, bytes]:
    oData = await wzry_api.get_user_role(yd_user_id)
    if isinstance(oData, int):
        return get_error(oData)

    data = oData[0]

    # 获取资料数据
    profile_data = await wzry_api.get_user_profile(yd_user_id, data['roleId'])

    # 获取段位数据
    profile_index_data = await wzry_api.get_user_profile_index(
        yd_user_id, data['roleId']
    )

    # 错误处理
    if isinstance(profile_data, int):
        return get_error(profile_data)

    if isinstance(profile_index_data, int):
        return get_error(profile_index_data)

    img = await get_color_bg(950, 2150, BG_PATH)
    img = img.filter(ImageFilter.GaussianBlur(28))

    avatar_url = profile_data["roleCard"]['roleBigIcon']
    avatar_img = await get_qq_avatar(avatar_url=avatar_url)
    avatar_img = await draw_pic_with_ring(avatar_img, 320)

    # 绘制title
    img.paste(avatar_img, (110, 70), avatar_img)
    title = Image.open(TEXT_PATH / 'title.png')
    img.paste(title, (-200, 405), title)

    img_draw = ImageDraw.Draw(img)
    img_draw.text(
        (275, 437), data['roleDesc'], (10, 10, 10), core_font(40), 'mm'
    )
    img_draw.text(
        (275, 495), data['roleName'], (48, 48, 48), core_font(30), 'mm'
    )

    # 标签画完

    # 段位
    x = 596
    y = -80

    flag_url: str = profile_data['roleCard']["flagImg"]
    flag_name = flag_url.split('/')[-1]
    flag_img = await download_file(flag_url, ICON_PATH, flag_name, (330, 634))
    img.paste(flag_img, (x, y), flag_img)
    img.paste(flag_img, (x, y + 360), flag_img)

    role_job_url = profile_data['roleCard']["roleJobIcon"]
    role_job_img = await get_pic(url=role_job_url, size=(400, 400))
    img.paste(role_job_img, (x - 35, y + 170), role_job_img)

    star_img_url: str = profile_data['roleCard']["starImg"]
    if star_img_url != '':
        sp_url = star_img_url.split('/')
        star_name = f'{sp_url[-1]}_{sp_url[-2]}'
        star_img = await download_file(
            star_img_url, ICON_PATH, star_name, (196, 72)
        )
        img.paste(star_img, (x + 65, y + 160), star_img)

    h = 445

    lstar_img = Image.open(TEXT_PATH / 'star.png')
    img.paste(lstar_img, (x + 120, h), lstar_img)

    img_draw.text(
        (x + 200, h + 25),
        "x" + str(profile_data['roleCard']['rankingStar']),
        (224, 195, 100),
        core_font(40),
        'mm',
    )

    # 巅峰赛
    profile_mods = profile_index_data['head']['mods']
    pinnacle_data = profile_mods[1]

    x = 596
    y = 340

    '''
    flag_img_url = profile_data['roleCard']["flagImg"]
    flag_img = await get_pic(url=flag_img_url, size=(330, 634))
    img.paste(flag_img, (x, y), flag_img)
    '''

    pinnacle_job_url = pinnacle_data['icon']
    sp_url = pinnacle_job_url.split('/')
    pinnacle_name = f'{sp_url[-1]}_{sp_url[-2]}'
    pinnacle_job_img = await download_file(
        pinnacle_job_url, ICON_PATH, pinnacle_name, (460, 460)
    )
    img.paste(pinnacle_job_img, (x - 65, y + 100), pinnacle_job_img)

    img_draw.text(
        (x + 163, 800),
        str(pinnacle_data['content']),
        (224, 195, 100),
        core_font(32),
        'mm',
    )
    # 上半部分结束

    # 总体资料
    battle_score: str = profile_mods[2]['content']  # 战斗力
    MVP: str = profile_mods[3]['content']  # MVP
    all_battle_num: str = profile_mods[4]['content']  # 总场次
    hero_num: str = profile_mods[5]['content']  # 英雄 11/115
    win_rate: str = profile_mods[6]['content']  # 胜率 51.85%
    skin_num: str = profile_mods[7]['content']  # 皮肤 11/522

    base_info_bg = Image.open(TEXT_PATH / 'base_info.png')
    info_draw = ImageDraw.Draw(base_info_bg)

    xoff = 174
    yoff = 132
    info_draw.text((122, 121), battle_score, 'black', core_font(39), 'mm')
    info_draw.text((122 + xoff, 121), MVP, 'black', core_font(39), 'mm')
    info_draw.text(
        (122 + xoff * 2, 121), all_battle_num, 'black', core_font(39), 'mm'
    )
    info_draw.text((122, 121 + yoff), hero_num, 'black', core_font(39), 'mm')
    info_draw.text(
        (122 + xoff, 121 + yoff), skin_num, 'black', core_font(39), 'mm'
    )
    info_draw.text(
        (122 + xoff * 2, 121 + yoff), win_rate, 'black', core_font(39), 'mm'
    )

    img.paste(base_info_bg, (0, 508), base_info_bg)

    # 常用英雄的排名
    x = 30
    y = 900
    hero_data = await wzry_api.get_user_profile_hero_list(
        yd_user_id, data['roleId']
    )
    if isinstance(hero_data, int):
        img_draw.text(
            (450, 1400),
            f'常用英雄获取失败,请前往王者营地开启陌生人可见:{hero_data}',
            (224, 200, 160),
            core_font(35),
            'mm',
        )
    else:
        hero_list = hero_data['heroList']
        char_mask = Image.open(TEXT_PATH / 'char_mask.png')
        content_font = core_font(46)

        for index, hero in enumerate(hero_list):
            char = Image.open(TEXT_PATH / 'char_bg.png')
            char_draw = ImageDraw.Draw(char)
            basic_info = hero['basicInfo']
            hero_img_url = get_hero_img_url(str(basic_info['heroId']))
            hero_img = await get_pic(hero_img_url, (270, 170))
            char.paste(hero_img, (57, 35), char_mask)

            char_draw.text(
                (395, 70),
                basic_info['title'],
                (0, 0, 0),
                core_font(48),
                'lm',
            )

            y += 42
            char_draw.text(
                (461, 144),
                str(basic_info['playNum']),
                (0, 0, 0),
                content_font,
                'mm',
            )
            char_draw.text(
                (635, 144),
                str(basic_info['winRate']),
                (0, 0, 0),
                content_font,
                'mm',
            )
            char_draw.text(
                (809, 144),
                str(basic_info['heroFightPower']),
                get_fight_color(basic_info['heroFightPower']),
                content_font,
                'mm',
            )

            # 画标
            honor = hero['honorTitle']
            if honor is not None:
                honor_bg_img_url = get_honor_bg_img_url(honor['type'])
                honor_bg_name = honor_bg_img_url.split('/')[-1]
                honor_bg_img = await download_file(
                    honor_bg_img_url, ICON_PATH, honor_bg_name, (64, 64)
                )
                honor_bg_img = honor_bg_img.convert('RGBA')
                char.paste(honor_bg_img, (260, 35), honor_bg_img)

                honor_img_url = get_honor_img_url(honor['type'])
                honor_img_name = honor_img_url.split('/')[-1]
                honor_img = await download_file(
                    honor_img_url, ICON_PATH, honor_img_name, (64, 52)
                )
                honor_img = honor_img.convert('RGBA')
                char.paste(honor_img, (260, 31), honor_img)

                char_draw.rounded_rectangle(
                    (641, 52, 905, 95),
                    20,
                    get_fight_color(basic_info['heroFightPower']),
                )
                char_draw.text(
                    (773, 75),
                    honor['desc']['abbr'],
                    'white',
                    core_font(36),
                    'mm',
                )

            img.paste(char, (0, 880 + index * 250), char)

    all_black = Image.new('RGBA', img.size, (255, 255, 255))
    img = Image.alpha_composite(all_black, img)
    return await convert_img(img)


def get_fight_color(power: int):
    if power <= 2500:
        return 47, 47, 47
    elif power <= 5000:
        return 69, 110, 232
    elif power <= 7500:
        return 91, 0, 227
    elif power <= 10000:
        return 252, 223, 119
    else:
        return 255, 54, 108


def get_honor_img_url(t: int):
    if t == 1:
        return "https://camp.qq.com/battle/home_v2/icon_honor_county.png"
    elif t == 2:
        return "https://camp.qq.com/battle/home_v2/icon_honor_city.png"
    elif t == 3:
        return "https://camp.qq.com/battle/home_v2/icon_honor_province.png"
    else:
        return "https://camp.qq.com/battle/home_v2/icon_honor_contry.png"


def get_honor_bg_img_url(t: int):
    return get_honor_img_url(t).replace("/icon", "/bg")


def get_hero_img_url(id: str):
    return (
        "https://game-1255653016.file.myqcloud.com/battle_skin_1250-326/"
        + id
        + "00.jpg?imageMogr2/thumbnail/x170/crop/"
        "270x170/gravity/east"
    )


async def get_pic_and_crop(
    url,
    box: Optional[Tuple[int, int, int, int]],
    size: Optional[Tuple[int, int]] = None,
):
    async with httpx.AsyncClient(timeout=None) as client:
        resp = await client.get(url=url)
        pic = Image.open(BytesIO(resp.read()))
        pic = pic.crop(box)
        pic = pic.convert("RGBA")
        if size is not None:
            pic = pic.resize(size, Image.LANCZOS)
        return pic
