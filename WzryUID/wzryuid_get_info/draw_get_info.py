from pathlib import Path
from typing import Union

from PIL import Image, ImageDraw

from gsuid_core.utils.fonts.fonts import core_font
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import (
    get_color_bg,
    get_qq_avatar,
    draw_pic_with_ring, get_pic,
)
from ..utils.error_reply import get_error
from ..utils.resource_path import BG_PATH
from ..utils.wzry_api import wzry_api

TEXT_PATH = Path(__file__).parent / 'texture2d'


async def draw_info_img(user_id: str, yd_user_id: str) -> Union[str, bytes]:
    oData = await wzry_api.get_user_role(yd_user_id)
    if isinstance(oData, int):
        return get_error(oData)

    data = oData[0]
    profile_data = await wzry_api.get_user_profile(yd_user_id, data['roleId'])

    img = await get_color_bg(950, 2000, BG_PATH, True)
    avatar_url = profile_data["roleCard"]['roleBigIcon']
    avatar_img = await get_qq_avatar(avatar_url=avatar_url)
    avatar_img = await draw_pic_with_ring(avatar_img, 320)
    img.paste(avatar_img, (310, 70), avatar_img)

    title = Image.open(TEXT_PATH / 'title.png')
    img.paste(title, (0, 405), title)

    img_draw = ImageDraw.Draw(img)
    img_draw.text((475, 437), data['roleDesc'], (10, 10, 10), core_font(40), 'mm')
    img_draw.text((475, 495), data['roleName'], (48, 48, 48), core_font(30), 'mm')
    ## 标签画完
    x = 50
    y = 540
    flag_img_url = profile_data['roleCard']["flagImg"]
    flag_img = await get_pic(url=flag_img_url, size=(330, 634))
    img.paste(flag_img, (x, y), flag_img)

    role_job_url = profile_data['roleCard']["roleJobIcon"]
    role_job_img = await get_pic(url=role_job_url, size=(400, 400))
    img.paste(role_job_img, (x-35, y + 220), role_job_img)

    star_img_url = profile_data['roleCard']["starImg"]
    star_img = await get_pic(url=star_img_url, size=(196, 72))
    img.paste(star_img, (x + 65, y + 210), star_img)

    lstar_img = Image.open(TEXT_PATH / 'star.png')
    img.paste(lstar_img, (x + 120, 1180), lstar_img)

    img_draw.text((x + 200, 1205), "x" + str(profile_data['roleCard']['rankingStar']),
                  (48, 48, 48), core_font(40), 'mm')
    ## 段位画完
    profile_index_data = await wzry_api.get_user_profile_index(yd_user_id, data['roleId'])
    profile_mods = profile_index_data['head']['mods']
    pinnacle_data = profile_mods[1]
    x = 580
    y = 540
    flag_img_url = profile_data['roleCard']["flagImg"]
    flag_img = await get_pic(url=flag_img_url, size=(330, 634))
    img.paste(flag_img, (x, y), flag_img)

    pinnacle_job_url = pinnacle_data['icon']
    pinnacle_job_img = await get_pic(url=pinnacle_job_url, size=(460, 460))
    img.paste(pinnacle_job_img, (x-65, y + 155), pinnacle_job_img)

    img_draw.text((x + 163, 880), str(pinnacle_data['content']), (224, 195, 151), core_font(32), 'mm')

    all_black = Image.new('RGBA', img.size, (255, 255, 255))
    img = Image.alpha_composite(all_black, img)
    return await convert_img(img)
