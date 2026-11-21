import time
import uuid
from copy import deepcopy
from typing import Any, Dict, Tuple, Union, Literal, Optional, cast

from gsuid_core.logger import logger
from aiohttp import (
    FormData,
    TCPConnector,
    ClientSession,
    ClientTimeout,
    ContentTypeError,
)

from ..database.models import WzryUser
from .model import SkinInfo, HeroRankList
from .api import (
    SKIN_LIST,
    USER_PROFILE,
    BATTLE_DETAIL,
    PROFILE_INDEX,
    BATTLE_HISTORY,
    HERO_RANK_LIST,
    ALL_ROLE_LIST_V3,
    PROFILE_HERO_LIST,
)


def generate_id():
    return str(uuid.uuid4()).replace("-", "").upper()


async def get_ck(
    target_user_id: Optional[str] = None,
) -> Union[int, Tuple[Optional[str], str]]:
    ck = await WzryUser.get_random_cookie(
        target_user_id if target_user_id else "18888888"
    )
    if ck is None:
        return -61
    wzUser = await WzryUser.base_select_data(cookie=ck)
    if wzUser is not None:
        uid = wzUser.uid
    else:
        return -61
    return uid, ck


class BaseWzryApi:
    ssl_verify = True
    _HEADER = {
        "Host": "kohcamp.qq.com",
        "origin": "https://kohcamp.qq.com",
        # "referer": "https://kohcamp.qq.com",
        "istrpcrequest": "true",
        "cchannelid": "2002",
        "cclientversioncode": "2047933506",
        "cclientversionname": "9.103.0723",
        "ccurrentgameid": "20001",
        "cgameid": "20001",
        "cgzip": "1",
        "cisarm64": "true",
        "crand": str(int(time.time())),
        "csupportarm64": "true",
        "csystem": "android",
        "csystemversioncode": "35",
        "csystemversionname": "15",
        "cpuhardware": "qcom",
        "gameareaid": "0",
        "gameid": "20001",
        "gameserverid": "0",
        "gameroleid": "0",
        # "gameopenid": generate_id(),
        "gameusersex": "1",
        "openid": generate_id(),
        "tinkerid": "2047933506_64_0",
        "content-encrypt": "",
        "accept-encrypt": "",
        "noencrypt": "1",
        "x-client-proto": "https",
        "content-type": "application/json; charset=UTF-8",
        "user-agent": "okhttp/4.9.1",
        "kohdimgender": "1",
    }

    async def get_battle_history(self, yd_user_id: str, option: int = 0):
        # 战绩列表走新版营地协议（新签名 + 响应解密），登录态复用账号池
        from ..camp_auth import MORE_BATTLE_LIST, camp_request

        body = {
            "lastTime": 0,
            "recommendPrivacy": 0,
            "apiVersion": 5,
            "friendUserId": yd_user_id,
            "option": option,
        }
        return await camp_request(MORE_BATTLE_LIST, body, yd_user_id)

    async def get_skin_list(self, yd_user_id: str) -> Union[int, SkinInfo]:
        # 皮肤墙走游戏侧 form 新协议（新版登录态 + 新客户端版本），登录态复用账号池
        from ..camp_auth import game_form_request

        result = await game_form_request(
            '/play/h5getheroskinlist',
            {
                'noCache': '0',
                'recommendPrivacy': '0',
                'friendUserId': yd_user_id,
            },
            yd_user_id,
        )
        if isinstance(result, int):
            return result
        return cast(SkinInfo, result)

    async def get_user_profile(self, yd_user_id: str, role_id: str):
        # 走新版营地协议，登录态复用账号池
        from ..camp_auth import camp_request

        return await camp_request(
            USER_PROFILE,
            {"friendUserId": yd_user_id, "roleId": role_id, "scenario": 0},
            yd_user_id,
        )

    async def get_user_profile_index(self, yd_user_id: str, role_id: str):
        # 走新版营地协议，登录态复用账号池
        from ..camp_auth import camp_request

        return await camp_request(
            PROFILE_INDEX,
            {
                "targetUserId": yd_user_id,
                "recommendPrivacy": 0,
                "targetRoleId": role_id,
                "apiVersion": 2,
                "resVersion": 3,
            },
            yd_user_id,
        )

    async def get_user_profile_hero_list(self, yd_user_id: str, role_id: str):
        # 走新版营地协议，登录态复用账号池
        from ..camp_auth import camp_request

        return await camp_request(
            PROFILE_HERO_LIST,
            {
                "targetUserId": yd_user_id,
                "recommendPrivacy": 0,
                "targetRoleId": role_id,
            },
            yd_user_id,
        )

    async def get_battle_detail(
        self,
        wz_user_id: str,
        gameSvr: str,
        relaySvr: str,
        gameSeq: str,
        battleType: int,
        yd_user_id: str = "",
    ):
        # 战绩详情走新版营地协议；yd_user_id 用于定位账号池登录态
        from ..camp_auth import BATTLE_DETAIL, camp_request

        body = {
            "recommendPrivacy": 0,
            "battleType": battleType,
            "gameSvr": gameSvr,
            "relaySvr": relaySvr,
            "targetRoleId": wz_user_id,
            "gameSeq": gameSeq,
        }
        return await camp_request(
            BATTLE_DETAIL, body, yd_user_id or wz_user_id
        )

    async def get_hero_rank_list(
        self,
        segment: int = 1,
        position: int = 0,
    ):
        '''
        segment: 5(赛事),4(顶端排位),3(巅峰赛1350),2(所有段位),1(所有段位)
        position: 5(打野),4(游走),3(发育),2(中路),1(对抗),0(全部)
        '''
        # 英雄榜是全局榜单，走新版营地协议，登录态用账号池的全局默认账号
        from ..camp_auth import camp_request, get_default_uid

        uid = get_default_uid()
        if not uid:
            return -61

        result = await camp_request(
            HERO_RANK_LIST,
            {
                "recommendPrivacy": 0,
                "segment": segment,
                "position": position,
            },
            uid,
        )
        if isinstance(result, Dict):
            return cast(HeroRankList, result)
        return result

    async def get_user_role(self, yd_user_id: str):
        # 角色列表走游戏侧 form 新协议，登录态复用账号池
        from ..camp_auth import game_form_request

        return await game_form_request(
            '/game/allrolelistv3',
            {'friendUserId': yd_user_id},
            yd_user_id,
        )

    def unpack(self, raw_data: Union[Dict, int, str]) -> Union[Dict, int]:
        if isinstance(raw_data, Dict):
            # 业务错误码可能是字符串（如 "-30003"），统一转为 int 交由 get_error 处理
            rc = raw_data.get("returnCode", 0)
            if rc not in (0, None) and "data" not in raw_data:
                try:
                    return int(rc)
                except (ValueError, TypeError):
                    return -1
            return raw_data.get("data", raw_data)
        elif isinstance(raw_data, str):
            # 字符串错误码（"_wzry_request" 在 returnCode 非 0 时原样返回）
            try:
                return int(raw_data)
            except ValueError:
                return -1
        return raw_data

    async def _wzry_request(
        self,
        url: str,
        method: Literal["GET", "POST"] = "GET",
        header: Dict[str, Any] = _HEADER,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Union[Dict[str, Any], str]] = None,
        data: Optional[FormData] = None,
    ) -> Union[Dict, int]:
        if "token" not in header and isinstance(json, Dict):
            target_user_id = (
                json["friendUserId"]
                if json and "friendUserId" in json
                else None
            )
            _i = await get_ck(target_user_id)
            if isinstance(_i, int):
                return _i
            header["token"] = _i[1]
            header["userid"] = _i[0]

        async with ClientSession(
            connector=TCPConnector(verify_ssl=self.ssl_verify)
        ) as client:
            async with client.request(
                method,
                url=url,
                headers=header,
                params=params,
                json=json,
                data=data,
                timeout=ClientTimeout(total=300),
            ) as resp:
                logger.debug(f'[Wzry] [URL] {url}')
                logger.debug(f'[Wzry] [HEADER] {header}')
                logger.debug(f'[Wzry] [PARAMS] {params}')
                logger.debug(f'[Wzry] [JSON] {json}')
                logger.debug(f'[Wzry] [DATA] {data}')

                try:
                    raw_data = await resp.json()
                except ContentTypeError:
                    _raw_data = await resp.text()
                    raw_data = {"retcode": -999, "data": _raw_data}
                logger.debug(raw_data)
                if raw_data and 'returnCode' in raw_data:
                    rc = raw_data['returnCode']
                    if rc not in (0, "0", None):
                        try:
                            return int(rc)
                        except (ValueError, TypeError):
                            return -1
                return raw_data
