from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.aps import scheduler
from gsuid_core.logger import logger

from ..utils.resource_path import TEMP_PATH
from .draw_hero_rank_list import draw_hero_rank_pic

sv_wzry_hero_data = SV('查询王者荣耀英雄热度')


@sv_wzry_hero_data.on_command(
    (
        '王者英雄热度榜',
        '王者英雄梯度榜',
        '王者梯度榜',
        '荣耀梯度榜',
        '荣耀热度榜',
    )
)
async def send_wzry_hero_data(bot: Bot, ev: Event):
    logger.info('[wzry] [英雄热度榜] 执行中...')
    im = await draw_hero_rank_pic(ev.text.strip())
    await bot.send(im)


@scheduler.scheduled_job('cron', hour=0, minute=5)
async def remove_cache():
    for item in TEMP_PATH.iterdir():
        if item.is_file():
            item.unlink()
