from enum import (
    Enum,
)
from typing import (
    Tuple,
)


class TransferPeriodEnum:
    """Перечисление периодов переноса."""

    OLD = 'old'
    NEW = 'new'

    values = {
        OLD: 'Старый период',
        NEW: 'Новый период',
    }


class LookupEnum(Enum):
    """Перечисление реализованных фильтров."""

    EQ = 'eq'
    IN = 'in'
    RANGE = 'range'

    @classmethod
    def get_all_str(cls) -> Tuple[str, ...]:
        """Возвращает все строковые представления."""
        return (
            cls.EQ.value,
            cls.IN.value,
            cls.RANGE.value,
        )
