from ..utils.database.models import WzryUser

ERROR_HINT = '添加失败，格式为:用户ID - Cookie\n例如:1810461245 - asRDmr5f'


async def deal_wz_ck(bot_id: str, cookie: str, user_id: str) -> str:
    if '-' not in cookie:
        return ERROR_HINT
    _ck = cookie.replace(' ', '').split('-')
    if len(_ck) != 2 or not _ck[0] or not _ck[0].isdigit() or not _ck[1]:
        return ERROR_HINT
    uid, ck = _ck[0], _ck[1]
    await WzryUser.insert_data(user_id, bot_id, cookie=ck, uid=uid)
    return '添加成功!'
