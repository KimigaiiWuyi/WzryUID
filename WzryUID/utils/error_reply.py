def get_error(retcode: int) -> str:
    if retcode == -41:
        return '你还没有绑定过uid哦!\n请使用[王者绑定UID]命令绑定!'
    elif retcode == -51:
        return '你还没有绑定过CK哦!\n请使用[王者添加CK]命令绑定!'
    elif retcode == -61:
        return '数据库不存在可用CK\n请使用[王者添加CK]命令绑定第一个CK!'
    else:
        return f'API报错, 错误码为{retcode}'
