"""新版王者荣耀营地接口客户端。

营地接口已升级：新版签名(encodeParam) + 新客户端版本号 + 响应体 XXTEA 加密。
协议细节参考 GloryOfKings-Plugin，但登录态存放在 WzryUID 自己的账号池
（data/WzryUID/AuthPool.json），与参考插件各自独立，不共享运行时文件。
"""

from __future__ import annotations

import json
import time
import uuid
import base64
import subprocess
from pathlib import Path
from typing import Any, Dict, Union, Optional

from gsuid_core.logger import logger
from gsuid_core.data_store import get_res_path

# WzryUID 自己的登录态账号池（gsuid_core data 目录下，已被 .gitignore 排除）
# 用 get_res_path 动态解析，不含任何其它项目的绝对路径，便于独立部署与推送 GitHub
AUTH_POOL_PATH = get_res_path('WzryUID') / 'AuthPool.json'
# 自包含 XXTEA helper
XXTEA_HELPER = Path(__file__).parent / 'xxtea_helper.js'
NODE_BIN = 'node'

# 新版营地协议固定参数（与参考插件一致）
BASE_URL = 'https://kohcamp.qq.com'
GAME_URL = 'https://ssl.kohsocialapp.qq.com:10001'
MORE_BATTLE_LIST = f'{BASE_URL}/game/morebattlelist'
BATTLE_DETAIL = f'{BASE_URL}/game/battledetail'

# 游戏侧 form 接口的公共头（与参考插件 gameFormHeaders 一致：全小写、无签名/traceparent）
GAME_FORM_HEADERS = {
    'Host': 'ssl.kohsocialapp.qq.com:10001',
    'content-encrypt': '',
    'accept-encrypt': '',
    'noencrypt': '1',
    'x-client-proto': 'https',
    'x-log-uid': '1245C88F-093D-406D-91F8-EB8D271D70DB',
    'kohdimgender': '2',
    'content-type': 'application/x-www-form-urlencoded',
    'accept-encoding': 'gzip',
    'user-agent': 'okhttp/4.9.1',
}

# 游戏侧 form body 的公共版本参数（新版客户端版本，与参考插件 baseConfig 一致）
GAME_FORM_FIELDS = {
    'cChannelId': '10003391',
    'cClientVersionCode': '2057957801',
    'cClientVersionName': '10.111.0323',
    'cCurrentGameId': '20001',
    'cGameId': '20001',
    'cGzip': '1',
    'cIsArm64': 'true',
    'cSupportArm64': 'true',
    'cSystem': 'android',
    'cSystemVersionCode': '34',
    'cSystemVersionName': '14',
    'cpuHardware': 'qcom',
    'gameAreaId': '1',
    'gameId': '20001',
    'gameRoleId': '0',
    'gameServerId': '0',
    'gameUserSex': '1',
    'openId': 'E66DC1CFC7F2EFA94561DD7F09EF7975',
    'tinkerId': '2057957801_64_0',
}

PUBLIC_HEADERS = {
    'origin': 'https://kohcamp.qq.com',
    'istrpcrequest': 'true',
    'cchannelid': '10003391',
    'cclientversioncode': '2057957801',
    'cclientversionname': '10.111.0323',
    'ccurrentgameid': '20001',
    'cgameid': '20001',
    'cgzip': '1',
    'cisarm64': 'true',
    'csupportarm64': 'true',
    'csystem': 'android',
    'csystemversioncode': '34',
    'csystemversionname': '14',
    'cpuhardware': 'qcom',
    'gameareaid': '1',
    'gameid': '20001',
    'gameserverid': '0',
    'gameroleid': '0',
    'gameusersex': '1',
    'tinkerid': '2057957801_64_0',
    'content-encrypt': '',
    'accept-encrypt': '',
    'noencrypt': '1',
    'x-client-proto': 'https',
    'content-type': 'application/json; charset=UTF-8',
    'user-agent': 'okhttp/4.9.1',
    'kohdimgender': '2',
}


def _xxtea(op: str, data_b64: str, key: str) -> str:
    """调用 Node helper 做 XXTEA 加解密，stdin 传数据避免命令行过长。"""
    result = subprocess.run(
        [NODE_BIN, str(XXTEA_HELPER), op, key],
        input=data_b64,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        raise RuntimeError(f'xxtea helper failed: {result.stderr.strip()}')
    return result.stdout.strip()


def get_default_uid() -> Optional[str]:
    """返回账号池里的全局默认账号营地 ID（供英雄榜等全局接口使用）。"""
    if not AUTH_POOL_PATH.exists():
        return None
    try:
        pool = json.loads(AUTH_POOL_PATH.read_text(encoding='utf-8'))
    except Exception:
        return None
    accounts = pool.get('accounts', {})
    # 优先标记为全局默认的账号
    for uid, auth in accounts.items():
        if auth.get('isGlobalDefault') and auth.get('token'):
            return str(uid)
    # 兜底：任意一个有 token 的账号
    for uid, auth in accounts.items():
        if auth.get('token') and not auth.get('authInvalid'):
            return str(uid)
    return None


def load_auth(uid: str) -> Optional[Dict[str, str]]:
    """按营地 ID 从 WzryUID 自己的账号池加载登录态。"""
    if not AUTH_POOL_PATH.exists():
        logger.warning(f'[WzryUID] 账号池不存在: {AUTH_POOL_PATH}')
        return None
    try:
        pool = json.loads(AUTH_POOL_PATH.read_text(encoding='utf-8'))
    except Exception as e:
        logger.warning(f'[WzryUID] 读取账号池失败: {e}')
        return None
    accounts = pool.get('accounts', {})
    auth = accounts.get(str(uid))
    if not auth or not auth.get('token'):
        logger.warning(f'[WzryUID] 账号池中无 uid={uid} 的登录态')
        return None
    return {
        'userId': str(auth.get('userId') or uid),
        'token': str(auth['token']),
        'userKey': str(auth.get('userKey') or ''),
    }


def _build_headers(auth: Dict[str, str]) -> Dict[str, str]:
    headers = dict(PUBLIC_HEADERS)
    headers['Host'] = 'kohcamp.qq.com'
    ts = int(time.time() * 1000)
    headers['crand'] = str(ts)
    headers['openid'] = uuid.uuid4().hex.upper()
    headers['token'] = auth['token']
    headers['userid'] = auth['userId']
    headers['x-log-uid'] = uuid.uuid4().hex.upper()
    headers['traceparent'] = (
        f'00-{uuid.uuid4().hex}{uuid.uuid4().hex[:16]}-'
        f'{uuid.uuid4().hex[:16]}-01'
    )
    # encodeParam: {timestamp, nonce} 用 userKey 做 XXTEA 加密后 base64
    user_key = auth.get('userKey', '')
    if user_key:
        payload = json.dumps(
            {
                'timestamp': ts,
                'nonce': f"{auth['userId']}:{uuid.uuid4().hex}:{ts}",
            },
            separators=(',', ':'),
        ).encode('utf-8')
        try:
            headers['encodeParam'] = _xxtea(
                'e', base64.b64encode(payload).decode(), user_key
            )
        except Exception as e:
            logger.warning(f'[WzryUID] 生成 encodeParam 失败: {e}')
    return headers


def _decode_response(text: str, user_key: str) -> Dict[str, Any]:
    """响应体在 campencrypt=true 时是 XXTEA 加密的 base64。"""
    if not user_key:
        raise RuntimeError('响应已加密但缺少 userKey')
    decrypted = _xxtea('d', text.strip(), user_key)
    raw = base64.b64decode(decrypted).rstrip(b'\x00').decode('utf-8', 'ignore')
    return json.loads(raw)


async def camp_request(
    url: str,
    body: Dict[str, Any],
    uid: str,
) -> Union[Dict[str, Any], int]:
    """发起新版营地请求，成功返回 data 字典，失败返回 int 错误码。"""
    import aiohttp

    auth = load_auth(uid)
    if auth is None:
        return -61  # 无可用登录态

    headers = _build_headers(auth)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=body,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                ret_header = resp.headers.get(
                    'returnCode'
                ) or resp.headers.get('returncode')
                text = await resp.text()
    except Exception as e:
        logger.warning(f'[WzryUID] 营地请求失败: {e}')
        return -1

    # 优先用响应头业务码判定（登录失效等业务错误常只有 header）
    if ret_header and str(ret_header) not in ('0', 'None'):
        try:
            return int(ret_header)
        except ValueError:
            pass

    try:
        if resp.headers.get('campencrypt') == 'true':
            data = _decode_response(text, auth['userKey'])
        else:
            data = json.loads(text) if text else {}
    except Exception as e:
        logger.warning(f'[WzryUID] 解析营地响应失败: {e}')
        return -1

    if not isinstance(data, dict):
        return -1

    rc = data.get('returnCode', 0)
    try:
        rc = int(rc)
    except (ValueError, TypeError):
        return -1
    if rc != 0:
        logger.warning(
            f'[WzryUID] 营地业务错误: {rc} {data.get("returnMsg", "")}'
        )
        return rc
    return data.get('data', data)


async def game_form_request(
    endpoint: str,
    extra_fields: Dict[str, Any],
    uid: str,
) -> Union[Dict[str, Any], int, list]:
    """游戏侧 form 接口（皮肤墙 / 角色列表等），响应不加密。

    :param endpoint: 形如 '/play/h5getheroskinlist'
    :param extra_fields: 该接口特有的表单字段（如 friendUserId）
    :param uid: 用于定位账号池登录态的营地 ID
    :return: data 字段（dict/list），失败返回 int 错误码
    """
    import aiohttp

    auth = load_auth(uid)
    if auth is None:
        return -61

    headers = dict(GAME_FORM_HEADERS)
    headers['token'] = auth['token']
    headers['userid'] = auth['userId']

    fields = dict(GAME_FORM_FIELDS)
    fields['cRand'] = str(int(time.time() * 1000))
    fields['token'] = auth['token']
    fields['userId'] = auth['userId']
    fields.update(extra_fields)

    url = f'{GAME_URL}{endpoint}'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                data=fields,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                text = await resp.text()
    except Exception as e:
        logger.warning(f'[WzryUID] 游戏侧 form 请求失败: {e}')
        return -1

    try:
        data = json.loads(text)
    except Exception as e:
        logger.warning(f'[WzryUID] 游戏侧 form 响应解析失败: {e}')
        return -1

    if not isinstance(data, dict):
        return -1
    rc = data.get('returnCode', 0)
    try:
        rc = int(rc)
    except (ValueError, TypeError):
        return -1
    if rc != 0:
        logger.warning(
            f'[WzryUID] 游戏侧 form 业务错误: {rc} {data.get("returnMsg", "")}'
        )
        return rc
    return data.get('data', data)
