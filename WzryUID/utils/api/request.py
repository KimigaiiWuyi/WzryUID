import time
import uuid
from copy import deepcopy
from typing import Any, Dict, Tuple, Union, Literal, Optional, cast

from gsuid_core.logger import logger
from aiohttp import FormData, TCPConnector, ClientSession, ContentTypeError

from .model import SkinInfo
from ..database.models import WzryUser
from .api import (
    SKIN_LIST,
    USER_PROFILE,
    BATTLE_DETAIL,
    PROFILE_INDEX,
    BATTLE_HISTORY,
    ALL_ROLE_LIST_V3,
    PROFILE_HERO_LIST,
)


def generate_id():
    return str(uuid.uuid4()).replace("-", "").upper()


async def get_ck(
    target_user_id: Optional[str] = None,
) -> Union[int, Tuple[str, str]]:
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
        "istrpcrequest": "true",
        "cchannelid": "10028581",
        "cclientversioncode": "2037857908",
        "cclientversionname": "7.84.0628",
        "ccurrentgameid": "20001",
        "cgameid": "20001",
        "cgzip": "1",
        "cisarm64": "true",
        "crand": str(int(time.time())),
        "csupportarm64": "true",
        "csystem": "android",
        "csystemversioncode": "33",
        "csystemversionname": "13",
        "cpuhardware": "qcom",
        "gameareaid": "1",
        "gameid": "20001",
        "gameopenid": generate_id(),
        "gameusersex": "1",
        "openid": generate_id(),
        "tinkerid": "2037857908_64_0",
        "content-encrypt": "",
        "accept-encrypt": "",
        "noencrypt": "1",
        "x-client-proto": "https",
        "content-type": "application/json; charset=UTF-8",
        "user-agent": "okhttp/4.9.1",
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
        header = deepcopy(self._HEADER)
        _i = await get_ck(yd_user_id)
        if isinstance(_i, int):
            return _i
        header["token"] = _i[1]
        header["userid"] = _i[0]

        header['content-type'] = 'application/x-www-form-urlencoded'

        data = FormData()
        data.add_fields(
            ('noCache', '0'),
            ('recommendPrivacy', '0'),
            # ('roleId', '957148943'),
            ('cChannelId', '10028581'),
            ('cClientVersionCode', '2037863508'),
            ('cClientVersionName', '7.84.0823'),
            ('cCurrentGameId', '20001'),
            ('cGameId', '20001'),
            ('cGzip', '1'),
            ('cIsArm64', 'false'),
            ('cRand', str(int(time.time()))),
            ('cSupportArm64', 'true'),
            ('cSystem', 'android'),
            ('cSystemVersionCode', '33'),
            ('cSystemVersionName', '13'),
            ('cpuHardware', 'qcom'),
            ('gameAreaId', '1'),
            ('gameId', '20001'),
            ('friendUserId', yd_user_id),
            # ('gameRoleId', '3731578254'),
            # ('gameServerId', '1469'),
            ('token', _i[1]),
            ('userId', _i[0]),
        )

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
            USER_PROFILE, "POST", header, None, data
        )
        return self.unpack(raw_data)

    async def get_user_profile_index(self, yd_user_id: str, role_id: str):
        header = deepcopy(self._HEADER)

        data = {
            "targetUserId": yd_user_id,
            "recommendPrivacy": 0,
            "targetRoleId": role_id,
        }
        raw_data = await self._wzry_request(
            PROFILE_INDEX, "POST", header, None, data
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
        header["token"] = ck
        header["userid"] = uid
        data = "friendUserId=" + yd_user_id + "&token=" + ck + "&userId=" + uid
        header["Content-Length"] = str(data.__len__())

        raw_data = await self._wzry_request0(
            ALL_ROLE_LIST_V3, "POST", header, None, data
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
        json: Optional[Dict[str, Any]] = None,
        data: Optional[FormData] = None,
    ) -> Union[Dict, int]:
        if "token" not in header:
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
                timeout=300,
            ) as resp:
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

    async def _wzry_request0(
        self,
        url: str,
        method: Literal["GET", "POST"] = "GET",
        header: Dict[str, Any] = _HEADER,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[FormData] = None,
    ) -> Union[Dict, int]:
        if "token" not in header:
            target_user_id = (
                data["friendUserId"]
                if data and "friendUserId" in data
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
                data=data,
                timeout=300,
            ) as resp:
                try:
                    raw_data = await resp.json()
                except ContentTypeError:
                    _raw_data = await resp.text()
                    raw_data = {"retcode": -999, "data": _raw_data}
                if (
                    raw_data
                    and 'returnCode' in raw_data
                    and raw_data['returnCode'] != 0
                ):
                    return raw_data['returnCode']
                logger.debug(raw_data)
                return raw_data
