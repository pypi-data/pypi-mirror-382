from django.apps import (
    AppConfig,
)


class FunctionToolsConfig(AppConfig):
    name = 'function_tools'
    label = 'function_tools'

    def __set_default_settings(self):
        """Установка дефолтных значений настроек приложения."""
        from django.conf import (
            settings,
        )

        from function_tools import (
            app_settings as defaults,
        )

        for name in dir(defaults):
            if name.isupper() and not hasattr(settings, name):
                setattr(settings, name, getattr(defaults, name))

    def ready(self):
        """Вызывается после инициализации приложения."""
        super().ready()

        # Установка дефолтных значений в settings.py
        self.__set_default_settings()
