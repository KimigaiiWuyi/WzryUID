error_code = {
    -41: '你还没有绑定过uid哦!\n请使用[王者绑定UID]命令绑定!',
    -51: '你还没有绑定过CK哦!\n请使用[王者添加CK]命令绑定!',
    -61: '数据库不存在可用CK\n请使用[王者添加CK]命令绑定第一个CK!',
    -30032: '用户不存在, 请检查是否绑定正确的UID(营地ID)\n可以使用[王者删除UID]命令删除错误的UID!',
    -30003: 'CK已失效, 请重新绑定。',
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
        return '你还没有绑定过CK哦!\n请使用[王者添加CK]命令绑定!'
    elif retcode == -61:
        return '数据库不存在可用CK\n请使用[王者添加CK]命令绑定第一个CK!'
    elif retcode == -30032:
        return '用户不存在, 请检查是否绑定正确的UID(营地ID)\n可以使用[王者删除UID]命令删除错误的UID!'
    elif retcode == -30003:
        return 'CK已失效, 请重新绑定。'
    elif retcode == -20011:
        return '参数异常，请检查源代码...'
    else:
        return f'API报错, 错误码为{retcode}'
