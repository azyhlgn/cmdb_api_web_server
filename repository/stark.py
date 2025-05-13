from stark.service.stark import site
from repository import models
from stark.service.stark import StarkModelConfig


class NicConfig(StarkModelConfig):
    add_btn = False


class IDCConfig(StarkModelConfig):
    display_list = [StarkModelConfig.display_checkbox, 'id', 'name', 'floor', StarkModelConfig.display_edit_delete]


site.register(models.IDC, IDCConfig)
site.register(models.Memory)
site.register(models.Disk)
site.register(models.NIC, NicConfig)
