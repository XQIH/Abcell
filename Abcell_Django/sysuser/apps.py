from django.apps import AppConfig


class SysuserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sysuser'
    
    def ready(self):
        # 确保只注册一次
        from django.contrib.auth import get_user_model
        get_user_model()
