from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger

from .get_help import get_wzry_core_help

sv_wzry_help = SV('王者帮助')


@sv_wzry_help.on_fullmatch(('王者帮助', '王者荣耀帮助'))
async def send_help_img(bot: Bot, ev: Event):
    logger.info('开始执行[王者帮助]')
    im = await get_wzry_core_help()
    await bot.send(im)
