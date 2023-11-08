from pathlib import Path
from typing import List, Union

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
from ..utils.api.model import SkinDetailAdd
from ..utils.resource_path import ICON_PATH, SKIN_PATH

sz_list = ['SR', 'S++', 'S+', 'S', 'A', 'B', 'C', 'D']

TEXT_PATH = Path(__file__).parent / 'texture2d'


async def _get_skin_list(user_id: str, yd_user_id: str) -> Union[str, bytes]:
    data = await wzry_api.get_skin_list(yd_user_id)
    if isinstance(data, int):
        return get_error(data)
    skin_info = data['skinCountInfo']
    not_for_sell: int = skin_info['notForSell']  # 非卖品
    total_value: int = skin_info['totalValue']  # 总价值
    owned: str = skin_info['owned']  # 已拥有
    # total_skin_num: int = skin_info['totalSkinNum']  # 全部
    # hero_type_list = skin_info['heroTypeList']
    # skin_type_list = skin_info['skinTypeList']

    sr_num = 0
    spp_num = 0
    sp_num = 0

    result: List[SkinDetailAdd] = []
    for skin in data['heroSkinList']:
        if 'iBuy' in skin:
            skin['szClass'] = skin['szClass'].replace('＋', '+')
            new_skin = data['heroSkinConfList'][skin['skinId']]
            if skin['szClass'] in sz_list:
                sz_c = skin['szClass']
                sz_level = sz_list.index(sz_c)
            else:
                sz_level = 7
            new_skin['iClass'] = sz_level  # type: ignore
            if sz_level == 0:
                sr_num += 1
            elif sz_level == 1:
                spp_num += 1
            elif sz_level == 2:
                sp_num += 1
            result.append(new_skin)  # type: ignore

    result = sorted(result, key=lambda x: x['iClass'])

    result = result[:42]

    h = 350 * ((len(result) - 1) // 6 + 1) + 900 + 80

    bg = await get_color_bg(1660, h, TEXT_PATH / 'BG', True)
    mask = Image.open(TEXT_PATH / 'mask.png')
    cover = Image.open(TEXT_PATH / 'cover.png')

    avatar_img = await get_qq_avatar(user_id)
    avatar_img = await draw_pic_with_ring(avatar_img, 400)

    title = Image.open(TEXT_PATH / 'title.png')
    title.paste(avatar_img, (620, 15), avatar_img)
    bg.paste(title, (0, 140), title)

    bg_draw = ImageDraw.Draw(bg)

    bg_draw.text(
        (840, 625), f'营地ID: {yd_user_id}', 'white', core_font(44), 'mm'
    )

    for i, text in enumerate(
        [owned, not_for_sell, total_value, sr_num, spp_num, sp_num]
    ):
        bg_draw.text(
            (256 + i * 231, 766), str(text), 'white', core_font(58), 'mm'
        )

    for index, skin in enumerate(result):
        base = 'https://game-1255653016.file.myqcloud.com'
        skin_img_url = f'{base}/battle_skin_702-1236/{skin["iSkinId"]}.jpg'
        # skin_img_url = skin['szLargeIcon']
        # skin_img_url = skin['szSmallIcon']
        sz = skin['szClass'].replace('＋', '+')  # 皮肤等级
        skin_bg = Image.open(TEXT_PATH / f'{sz}.png')
        sz_title = skin['szTitle']  # 皮肤名
        hero_name = skin['szHeroTitle']  # 英雄名
        # worth = skin['skin_worth']

        skin_img = await download_file(
            skin_img_url,
            SKIN_PATH,
            f'{sz_title}_{skin["iSkinId"]}.png',
            (216, 384),
        )

        skin_bg.paste(skin_img, (22, 3), mask)
        skin_bg.paste(cover, (0, 0), cover)

        if skin['classLabel']:
            label_name = skin['classLabel'].split('/')[-1]
            label: Image.Image = await download_file(
                skin['classLabel'], ICON_PATH, label_name
            )  # type:ignore
            if label.size == (95, 46):
                skin_bg.paste(label, (128, 53), label)
            elif label.size == (120, 38) or label.size == (128, 38):
                skin_bg.paste(label, (102, 57), label)
            elif label.size == (300, 95):
                label = label.resize((120, 38))
                skin_bg.paste(label, (128, 53), label)
            else:
                new_size = (int(label.size[0] / 2), int(label.size[1] / 2))
                label = label.resize(new_size)
                skin_bg.paste(label, (102, 57), label)

        skin_draw = ImageDraw.Draw(skin_bg)
        skin_draw.text((40, 290), sz_title, (0, 209, 255), core_font(30), 'lm')
        skin_draw.text(
            (40, 322), hero_name, (235, 235, 235), core_font(22), 'lm'
        )

        x_offset = (index % 6) * 250 + 80
        y_offset = (index // 6) * 350 + 900
        bg.paste(skin_bg, (x_offset, y_offset), skin_bg)

    bg_draw.text(
        (840, h - 35),
        'Power by Wuyi无疑 & Created by GsCore & WzryUID',
        (220, 220, 220),
        core_font(22),
        'mm',
    )

    # 最后生成图片
    all_black = Image.new('RGBA', bg.size, (0, 0, 0))
    bg = Image.alpha_composite(all_black, bg)

    return await convert_img(bg)
