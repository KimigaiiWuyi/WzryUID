from pathlib import Path
from typing import List, Union

from PIL import Image, ImageDraw
from gsuid_core.utils.fonts.fonts import core_font
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import get_color_bg

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
    total_skin_num: int = skin_info['totalSkinNum']  # 全部
    # hero_type_list = skin_info['heroTypeList']
    # skin_type_list = skin_info['skinTypeList']

    result: List[SkinDetailAdd] = []
    for skin in data['heroSkinConfList'].values():
        i_buy = skin['iBuy']
        if i_buy:
            skin['szClass'] = skin['szClass'].replace('＋', '+')
            sz = skin['szClass']  # 皮肤等级
            if sz:
                skin['level'] = sz_list.index(sz)  # type: ignore
            else:
                skin['level'] = 7  # type: ignore
                skin['szClass'] = 'D'
            result.append(skin)  # type: ignore

    h = 370 * ((len(result) - 1) // 5 + 1)

    bg = await get_color_bg(1300, h, TEXT_PATH / 'BG', True)
    mask = Image.open(TEXT_PATH / 'mask.png')
    cover = Image.open(TEXT_PATH / 'cover.png')

    for index, skin in enumerate(result):
        skin_img_url = f'https://game-1255653016.file.myqcloud.com/battle_skin_702-1236/{skin["iSkinId"]}.jpg'
        # skin_img_url = skin['szLargeIcon']
        # skin_img_url = skin['szSmallIcon']
        sz = skin['szClass']  # 皮肤等级
        skin_bg = Image.open(TEXT_PATH / f'{sz}.png')
        sz_title = skin['szTitle']  # 皮肤名
        hero_name = skin['szHeroTitle']  # 英雄名
        # worth = skin['skin_worth']

        skin_img = await download_file(
            skin_img_url, SKIN_PATH, f'{sz_title}.png', (216, 384)
        )
        '''
        skin_img = await download_file(
            skin_img_url, SKIN_PATH, f'{sz_title}.png', (229, 305)
        )
        '''

        skin_bg.paste(skin_img, (22, 3), mask)
        skin_bg.paste(cover, (0, 0), cover)

        if skin['classLabel']:
            label_name = skin['classLabel'].split('/')[-1]
            label = await download_file(
                skin['classLabel'], ICON_PATH, label_name, (120, 38)
            )
            skin_bg.paste(label, (269, 189), label)

        skin_draw = ImageDraw.Draw(skin_bg)
        skin_draw.text((40, 290), sz_title, (0, 209, 255), core_font(30), 'lm')
        skin_draw.text(
            (40, 322), hero_name, (235, 235, 235), core_font(22), 'lm'
        )

        x_offset = (index % 5) * 260
        y_offset = (index // 5) * 370
        bg.paste(skin_bg, (x_offset, y_offset), skin_bg)
        
    return await convert_img(bg)
