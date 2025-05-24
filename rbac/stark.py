from stark.service.stark import site, StarkModelConfig
from rbac.models import UserInfo, Role, Permission


class RoleConfig(StarkModelConfig):
    display_list = ['name', StarkModelConfig.display_edit_delete]


site.register(UserInfo)
site.register(Role, RoleConfig)
site.register(Permission)
