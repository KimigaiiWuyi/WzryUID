from typing import Optional

from sqlmodel import Field
from gsuid_core.utils.database.base_models import Bind, User
from gsuid_core.webconsole.mount_app import PageSchema, GsAdminModel, site


class WzryBind(Bind, table=True):
    uid: Optional[str] = Field(default=None, title='王者荣耀UID')


class WzryUser(User, table=True):
    uid: Optional[str] = Field(default=None, title='王者荣耀UID')


@site.register_admin
class WzryBindadmin(GsAdminModel):
    pk_name = 'id'
    page_schema = PageSchema(label='王者绑定管理', icon='fa fa-users')

    # 配置管理模型
    model = WzryBind


@site.register_admin
class WzryUseradmin(GsAdminModel):
    pk_name = 'id'
    page_schema = PageSchema(label='王者CK管理', icon='fa fa-database')

    # 配置管理模型
    model = WzryUser
