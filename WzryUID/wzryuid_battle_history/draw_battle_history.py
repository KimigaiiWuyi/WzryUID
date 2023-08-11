from pathlib import Path
from typing import Tuple, Union

from PIL import Image, ImageDraw
from gsuid_core.utils.fonts.fonts import core_font
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import (
    get_color_bg,
    get_qq_avatar,
    draw_pic_with_ring,
)

from ..utils.wzry_api import wzry_api
from ..utils.error_reply import get_error
from ..utils.download import download_file
from ..utils.resource_path import BG_PATH, ICON_PATH, AVATAR_PATH

TEXT_PATH = Path(__file__).parent / 'texture2d'


async def draw_history_img(user_id: str, yd_user_id: str) -> Union[str, bytes]:
    data = await wzry_api.get_battle_history(yd_user_id)
    if isinstance(data, int):
        return get_error(data)

    game_text = '正在游戏' if data['isGaming'] else '当前未在游戏中'

    battle_data = data['list'][:12]

    if len(battle_data) < 12:
        h = 500 + len(battle_data) * 120 + 60
    else:
        h = 2000

    img = await get_color_bg(950, h, BG_PATH, True)
    avatar_img = await get_qq_avatar(user_id)
    avatar_img = await draw_pic_with_ring(avatar_img, 320)

    title = Image.open(TEXT_PATH / 'title.png')
    ring = Image.open(TEXT_PATH / 'avatar_ring.png')

    img.paste(avatar_img, (310, 70), avatar_img)
    img.paste(title, (0, 405), title)
    hero_mask = Image.open(TEXT_PATH / 'avatar_mask.png')

    text_color = (48, 48, 48)
    for index, battle in enumerate(battle_data):
        is_win = True if battle['gameresult'] == 1 else False
        date = battle["gametime"]
        if is_win:
            bar_text = '胜利'
            babg = Image.open(TEXT_PATH / 'win_bg.png')
            bar_color = (66, 183, 255)
        else:
            bar_text = '失败'
            babg = Image.open(TEXT_PATH / 'lose_bg.png')
            bar_color = (255, 66, 66)

        hero_path = AVATAR_PATH / f'{battle["heroId"]}.png'
        if not hero_path.exists():
            await download_file(
                battle["heroIcon"], AVATAR_PATH, f'{battle["heroId"]}.png'
            )

        hero_img = Image.open(hero_path).resize((100, 100))
        babg.paste(hero_img, (79, 9), hero_mask)
        babg.paste(ring, (78, 8), ring)

        babg_draw = ImageDraw.Draw(babg)

        kill = battle['killcnt']
        dead = battle['deadcnt']
        assist = battle['assistcnt']

        babg_draw.text((210, 50), bar_text, bar_color, core_font(32), 'lm')
        babg_draw.text(
            (281, 52), battle['mapName'], text_color, core_font(18), 'lm'
        )

        if battle["desc"] != "":
            babg_draw.rectangle(
                (395, 45, 495, 85),
                fill=(255, 247, 247, 33),
                outline=(0, 0, 0, 33),
                width=2,
            )
            babg_draw.text(
                (405, 65), battle['desc'], bar_color, core_font(26), 'lm'
            )

        babg_draw.text(
            (210, 83),
            f"{kill} / {dead} / {assist}",
            text_color,
            core_font(33),
            'lm',
        )
        babg_draw.text((855, 94), date, text_color, core_font(20), 'rm')

        if battle['evaluateUrlV2']:
            await paste_icon(battle['evaluateUrlV2'], babg, (622, 33))

        if battle['mvpUrlV2']:
            await paste_icon(battle['mvpUrlV2'], babg, (763, 33))

        img.paste(babg, (0, 540 + index * 120), babg)

    img_draw = ImageDraw.Draw(img)
    img_draw.text((475, 437), '王者荣耀战绩', (10, 10, 10), core_font(40), 'mm')
    img_draw.text((475, 495), game_text, text_color, core_font(30), 'mm')
    all_black = Image.new('RGBA', img.size, (255, 255, 255))
    img = Image.alpha_composite(all_black, img)
    return await convert_img(img)


async def paste_icon(url: str, img: Image.Image, pos: Tuple[int, int]):
    icon_name: str = url.split('/')[-1]
    path = ICON_PATH / icon_name
    if not path.exists():
        await download_file(url, ICON_PATH, icon_name)
    eval_icon = Image.open(path)
    eval_icon = eval_icon.resize(
        (int(eval_icon.size[0] * 0.7), int(eval_icon.size[1] * 0.7))
    )
    img.paste(eval_icon, pos, eval_icon)
