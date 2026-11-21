# 查询失败时的用户提示。
# 注意：新版协议下查询首选由 WzryScanLogin 扫码写入账号池的登录态
# （data/WzryUID/AuthPool.json）；旧的「王者添加CK」作为备用方式仅写数据库。
# 因此与登录态相关的错误优先引导用户使用扫码登录。
SCAN_LOGIN_HINT = '请使用[王者扫码登录]扫码获取登录态(需安装 WzryScanLogin 插件)'

error_code = {
    -41: '你还没有绑定过uid哦!\n请使用[王者绑定UID]命令绑定!',
    -51: f'你还没有可用的登录态哦!\n{SCAN_LOGIN_HINT}!',
    -61: f'账号池中没有可用的登录态!\n{SCAN_LOGIN_HINT}!',
    -30032: '用户不存在, 请检查是否绑定正确的UID(营地ID)\n可以使用[王者删除UID]命令删除错误的UID!',
    -30003: f'登录态已失效, 请重新扫码。\n{SCAN_LOGIN_HINT}!',
    -20011: '参数异常，请检查源代码...',
    -30087: '该用户暂无角色...请检查UID是否正确。',
    -47004: '该召唤师隐藏了皮肤列表, 无法查看。',
}


def get_error(retcode: int) -> str:
    if retcode in error_code:
        return error_code[retcode]

    if retcode == -41:
        return '你还没有绑定过uid哦!\n请使用[王者绑定UID]命令绑定!'
    elif retcode == -51:
        return f'你还没有可用的登录态哦!\n{SCAN_LOGIN_HINT}!'
    elif retcode == -61:
        return f'账号池中没有可用的登录态!\n{SCAN_LOGIN_HINT}!'
    elif retcode == -30032:
        return '用户不存在, 请检查是否绑定正确的UID(营地ID)\n可以使用[王者删除UID]命令删除错误的UID!'
    elif retcode == -30003:
        return f'登录态已失效, 请重新扫码。\n{SCAN_LOGIN_HINT}!'
    elif retcode == -20011:
        return '参数异常，请检查源代码...'
    else:
        return f'API报错, 错误码为{retcode}'
