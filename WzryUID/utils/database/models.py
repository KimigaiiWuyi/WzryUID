from gsuid_core.utils.database.base_models import Bind, User
from typing import Optional
from sqlmodel import Field


class WzryBind(Bind, table=True):
    uid: Optional[str] = Field(default=None, title='王者荣耀UID')


class WzryUser(User, table=True):
    uid: Optional[str] = Field(default=None, title='王者荣耀UID')
    pass
