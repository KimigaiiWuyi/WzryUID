from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.utils.database.api import get_uid
from .draw_battle_history import draw_history_img
from ..utils.database.models import WzryBind
from ..utils.error_reply import get_error

sv_wzry_history_filter = SV('查询王者荣耀战绩', priority=10)
sv_wzry_history = SV('查询王者荣耀战绩')


@sv_wzry_history_filter.on_prefix(('查荣耀'))
async def send_wzry_history(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev, WzryBind)
    if uid is None:
        return await bot.send(get_error(-41))
    name = ev.text.strip()
    option = 0
    if name.startswith("排位"):
        option = 1
    elif name.startswith("娱乐"):
        option = 3
    elif name.startswith("巅峰"):
        option = 4
    logger.info(f'[查荣耀] uid:{uid}')
    im = await draw_history_img(ev.user_id, uid, option)
    await bot.send(im)


@sv_wzry_history.on_command(('查荣耀'))
async def send_wzry_history(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev, WzryBind)
    if uid is None:
        return await bot.send(get_error(-41))
    logger.info(f'[查荣耀] uid:{uid}')
    im = await draw_history_img(ev.user_id, uid)
    await bot.send(im)
