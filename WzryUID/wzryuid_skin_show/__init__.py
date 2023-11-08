from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.database.api import get_uid

from ..utils.error_reply import get_error
from .get_skin_list import _get_skin_list
from ..utils.database.models import WzryBind

sv_wzry_skin_list = SV('查询王者荣耀皮肤列表')


@sv_wzry_skin_list.on_command('皮肤墙')
async def send_wzry_skin_list(bot: Bot, ev: Event):
    user_id = ev.at if ev.at else ev.user_id
    uid = await get_uid(bot, ev, WzryBind)
    if uid is None:
        return await bot.send(get_error(-41))
    logger.info(f'[皮肤墙] uid:{uid}')
    im = await _get_skin_list(user_id, uid)
    await bot.send(im)
