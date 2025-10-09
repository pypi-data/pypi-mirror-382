from typing import (
    Optional,
    Type,
    Union,
)

from function_tools.caches import (
    BaseCache,
    CacheStorage,
)


class BaseHelper:
    """Базовый класс помощника.

    Предполагается, что у наследников будут создаваться кеши и собираться прочая вспомогательная информация, которая
    требуется для исполнения действий.

    is_force_fill_cache указывает, что необходимо наполнить кеш при его инициализации.
    """

    def __init__(self, *args, is_force_fill_cache: bool = True, **kwargs):
        super().__init__()

        self._cache_class = self._prepare_cache_class()

        self._cache: Optional[Union[BaseCache, CacheStorage]] = None

        self._prepare_cache(*args, **kwargs)

        if is_force_fill_cache:
            self.fill_cache()

    @property
    def cache(self):
        """Возвращает кеш помощника."""
        return self._cache

    def _prepare_cache_class(self) -> Union[Optional[Type[BaseCache]], Optional[Type[CacheStorage]]]:
        """Возвращает класс кеша помощника."""
        return BaseCache

    def _prepare_cache(self, *args, **kwargs):
        """Метод создания кеша.

        Кеш хранится в публичном свойстве cache. По умолчанию добавлена
        заглушка.
        """
        if issubclass(self._cache_class, (BaseCache, CacheStorage)):
            self._cache = self._cache_class(*args, **kwargs)
        else:
            self._cache = BaseCache(*args, **kwargs)

    def fill_cache(self, *args, **kwargs):
        """Насыщение кеша данными."""
        self._cache.prepare(*args, **kwargs)


class BaseRunnerHelper(BaseHelper):
    """Базовый класс помощника ранера выполнения функций."""


class BaseFunctionHelper(BaseHelper):
    """Базовый класс помощника функции.

    Предполагается, что в наследниках будут создаваться кеши и собираться прочая вспомогательная информация, которая
    требуется для исполнения функции.
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
