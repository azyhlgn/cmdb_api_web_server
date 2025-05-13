from django.apps import AppConfig


class StarkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stark'

    def ready(self):
        # 用于自动发现每个app下的stark文件并执行
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('stark')
