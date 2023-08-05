import time
import uuid
from copy import deepcopy
from typing import Any, Dict, Union, Literal, Optional

from gsuid_core.logger import logger
from aiohttp import TCPConnector, ClientSession, ContentTypeError

from ..database.models import WzryUser
from .api import BATTLE_DETAIL, BATTLE_HISTORY


def generate_id():
    return str(uuid.uuid4()).replace("-", "").upper()


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

    async def get_battle_history(self, yd_user_id: str):
        header = deepcopy(self._HEADER)
        # header['gameserverid'] = '1469'
        # header['gameroleid'] = '3731578254'

        data = {
            "lastTime": 0,
            "recommendPrivacy": 0,
            "apiVersion": 5,
            # 'friendRoleId': '3731578254',
            "friendUserId": yd_user_id,
            "option": 0,
        }
        raw_data = await self._wzry_request(
            BATTLE_HISTORY, "POST", header, None, data
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
        data: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict, int]:
        if "token" not in header:
            target_user_id = (
                data["friendUserId"]
                if data and "friendUserId" in data
                else None
            )
            ck = await WzryUser.get_random_cookie(
                target_user_id if target_user_id else "18888888"
            )
            if ck is None:
                return -61
            wzUser = await WzryUser.base_select_data(WzryUser, cookie=ck)
            if wzUser is not None:
                uid = wzUser.uid
            else:
                return -61
            header["token"] = ck
            header["userid"] = uid

        async with ClientSession(
            connector=TCPConnector(verify_ssl=self.ssl_verify)
        ) as client:
            async with client.request(
                method,
                url=url,
                headers=header,
                params=params,
                json=data,
                timeout=300,
            ) as resp:
                try:
                    raw_data = await resp.json()
                except ContentTypeError:
                    _raw_data = await resp.text()
                    raw_data = {"retcode": -999, "data": _raw_data}
                logger.debug(raw_data)
                return raw_data
