from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from ..utils.database.models import WzryBind
from gsuid_core.utils.message import send_diff_msg
from .deal_ck import deal_wz_ck

wzry_user_info = SV('王者用户绑定')
wzry_cookie_add = SV('王者CK添加')


@wzry_user_info.on_command(
    (
        '王者绑定',
        '王者绑定uid',
        '王者绑定UID',
        '王者切换',
        '王者切换uid',
        '王者切换UID',
        '王者删除uid',
        '王者删除UID',
    )
)
async def send_wz_link_uid_msg(bot: Bot, ev: Event):
    await bot.logger.info('开始执行[绑定/解绑用户信息]')
    qid = ev.user_id
    await bot.logger.info('[绑定/解绑]UserID: {}'.format(qid))

    uid = ev.text.strip()
    if uid and not uid.isdigit():
        return await bot.send('你输入了错误的格式!')

    if '绑定' in ev.command:
        data = await WzryBind.insert_uid(qid, ev.bot_id, uid, ev.group_id)
        return await send_diff_msg(
            bot,
            data,
            {
                0: f'绑定UID{uid}成功！',
                -1: f'UID{uid}的位数不正确！',
                -2: f'UID{uid}已经绑定过了！',
                -3: '你输入了错误的格式!',
            },
        )
    elif '切换' in ev.command:
        retcode = await WzryBind.switch_uid_by_game(qid, ev.bot_id, uid)
        if retcode == 0:
            return await bot.send(f'切换UID{uid}成功！')
        else:
            return await bot.send(f'尚未绑定该UID{uid}')
    else:
        data = await WzryBind.delete_uid(qid, ev.bot_id, uid)
        return await send_diff_msg(
            bot,
            data,
            {
                0: f'删除UID{uid}成功！',
                -1: f'该UID{uid}不在已绑定列表中！',
            },
        )


@wzry_cookie_add.on_prefix(('王者添加ck', '王者添加CK'))
async def send_wz_add_ck_msg(bot: Bot, ev: Event):
    im = await deal_wz_ck(ev.bot_id, ev.text, ev.user_id)
    await bot.send(im)
