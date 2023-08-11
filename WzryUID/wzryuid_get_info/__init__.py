from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.database.api import get_uid

from .draw_get_info import draw_info_img
from ..utils.error_reply import get_error
from ..utils.database.models import WzryBind

sv_wzry_get_info = SV('查询王者荣耀主页详细信息')


# 1. 获取用户 大区 等信息
# 2. 获取常用英雄
# 3. 获取段位.巅峰赛
@sv_wzry_get_info.on_command('当前段位')
async def send_wzry_history(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev, WzryBind)
    if uid is None:
        return await bot.send(get_error(-41))
    logger.info(f'[当前段位] uid:{uid}')
    im = await draw_info_img(ev.user_id, uid)
    await bot.send(im)
