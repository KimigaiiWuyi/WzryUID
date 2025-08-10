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
        header = deepcopy(self._HEADER)
        # header['gameserverid'] = '1469'
        # header['gameroleid'] = '3731578254'

        data = {
            "lastTime": 0,
            "recommendPrivacy": 0,
            "apiVersion": 5,
            # 'friendRoleId': '3731578254',
            "friendUserId": yd_user_id,
            "option": option,
        }
        raw_data = await self._wzry_request(
            BATTLE_HISTORY, "POST", header, None, data
        )
        return self.unpack(raw_data)

    async def get_skin_list(self, yd_user_id: str) -> Union[int, SkinInfo]:
        # header = deepcopy(self._HEADER)
        _i = await get_ck(yd_user_id)
        if isinstance(_i, int):
            return _i

        if _i[0] is None:
            return -61

        header: Dict[str, Any] = {
            "content-encrypt": "",
            "accept-encrypt": "",
            "noencrypt": "1",
            "x-client-proto": "https",
            "x-log-uid": "1245C88F-093D-406D-91F8-EB8D271D70DB",
            "kohdimgender": "1",
            "content-type": "application/x-www-form-urlencoded",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.9.1",
        }

        header["token"] = _i[1]
        header["userid"] = _i[0]

        data = FormData()
        data.add_field("noCache", "0")
        data.add_field("recommendPrivacy", "0")
        data.add_field('friendUserId', yd_user_id)
        data.add_field("cChannelId", "2002")
        data.add_field("cClientVersionCode", "2047933506")
        data.add_field("cClientVersionName", "9.103.0723")
        data.add_field("cCurrentGameId", "20001")
        data.add_field("cGameId", "20001")
        data.add_field("cGzip", "1")
        data.add_field("cIsArm64", "true")
        data.add_field("cRand", "1754809059114")
        data.add_field("cSupportArm64", "true")
        data.add_field("cSystem", "android")
        data.add_field("cSystemVersionCode", "35")
        data.add_field("cSystemVersionName", "15")
        data.add_field("cpuHardware", "qcom")
        data.add_field("gameAreaId", "0")
        data.add_field("gameId", "20001")
        data.add_field("gameRoleId", "0")
        data.add_field("gameServerId", "0")
        data.add_field("gameUserSex", "1")
        data.add_field("openId", "E66DC1CFC7F2EFA94561DD7F09EF7975")
        data.add_field("tinkerId", "2047933506_64_0")
        data.add_field(
            "token",
            _i[1],
        )
        data.add_field("userId", _i[0])

        raw_data = await self._wzry_request(
            SKIN_LIST, "POST", header, None, data=data
        )
        if not isinstance(raw_data, int):
            return cast(SkinInfo, raw_data['data'])
        return raw_data

    async def get_user_profile(self, yd_user_id: str, role_id: str):
        header = deepcopy(self._HEADER)

        data = {"friendUserId": yd_user_id, "roleId": role_id, "scenario": 0}
        raw_data = await self._wzry_request(
            USER_PROFILE,
            "POST",
            header,
            None,
            data,
        )
        return self.unpack(raw_data)

    async def get_user_profile_index(self, yd_user_id: str, role_id: str):
        header = deepcopy(self._HEADER)

        data = {
            "targetUserId": yd_user_id,
            "recommendPrivacy": 0,
            "targetRoleId": role_id,
            "apiVersion": 2,
            "resVersion": 3,
            # "itsMe": False,
        }
        raw_data = await self._wzry_request(
            PROFILE_INDEX,
            "POST",
            header,
            None,
            data,
        )
        return self.unpack(raw_data)

    async def get_user_profile_hero_list(self, yd_user_id: str, role_id: str):
        header = deepcopy(self._HEADER)

        data = {
            "targetUserId": yd_user_id,
            "recommendPrivacy": 0,
            "targetRoleId": role_id,
        }
        raw_data = await self._wzry_request(
            PROFILE_HERO_LIST, "POST", header, None, data
        )
        return self.unpack(raw_data)

    async def get_battle_detail(
        self,
        wz_user_id: str,
        gameSvr: str,
        relaySvr: str,
        gameSeq: str,
        battleType: int,
    ):
        header = deepcopy(self._HEADER)
        # header['gameserverid'] = '1469'
        # header['gameroleid'] = '3731578254'

        data = {
            "recommendPrivacy": 0,
            "battleType": battleType,
            "gameSvr": gameSvr,
            "relaySvr": relaySvr,
            "targetRoleId": wz_user_id,
            "gameSeq": gameSeq,
        }

        raw_data = await self._wzry_request(
            BATTLE_DETAIL, "POST", header, None, data
        )
        return self.unpack(raw_data)

    async def get_hero_rank_list(
        self,
        segment: int = 1,
        position: int = 0,
    ):
        '''
        segment: 5(赛事),4(顶端排位),3(巅峰赛1350),2(所有段位),1(所有段位)
        position: 5(打野),4(游走),3(发育),2(中路),1(对抗),0(全部)
        '''
        header = deepcopy(self._HEADER)

        data = {
            "recommendPrivacy": 0,
            "segment": segment,
            "position": position,
        }

        raw_data = await self._wzry_request(
            HERO_RANK_LIST, "POST", header, None, data
        )
        if isinstance(raw_data, Dict):
            return cast(HeroRankList, raw_data['data'])
        return raw_data

    async def get_user_role(self, yd_user_id: str):
        header = deepcopy(self._HEADER)
        header["Content-Type"] = "application/x-www-form-urlencoded"
        header["Host"] = "ssl.kohsocialapp.qq.com:10001"
        ck = await WzryUser.get_random_cookie(yd_user_id)
        if ck is None:
            return -61
        wzUser = await WzryUser.base_select_data(cookie=ck)
        if wzUser is not None:
            uid = wzUser.uid
        else:
            return -61

        if uid is None:
            return -61

        header["token"] = ck
        header["userid"] = uid
        form_data = FormData()
        form_data.add_field("friendUserId", yd_user_id)
        form_data.add_field("token", ck)
        form_data.add_field("userId", uid)

        # data = "friendUserId=" + yd_user_id + "&token=" + ck + "&userId=" + uid
        # header["Content-Length"] = str(data.__len__())

        raw_data = await self._wzry_request(
            ALL_ROLE_LIST_V3,
            "POST",
            header,
            None,
            None,
            form_data,
        )
        return self.unpack(raw_data)

    def unpack(self, raw_data: Union[Dict, int]) -> Union[Dict, int]:
        if isinstance(raw_data, Dict):
            return raw_data["data"]
        else:
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
                if (
                    raw_data
                    and 'returnCode' in raw_data
                    and raw_data['returnCode'] != 0
                ):
                    return raw_data['returnCode']
                return raw_data
                return raw_data
