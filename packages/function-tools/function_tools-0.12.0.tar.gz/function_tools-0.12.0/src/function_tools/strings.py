SEARCHING_KEY_SIZE_MORE_THAN_DEFAULT_SEARCHING_KEY_ERROR = (
    'Ключ для поиска не может быть больше, чем ключ, на основе которого была построена хеш-таблица!'
)

SEARCHING_KEY_SIZE_LESS_THAN_DEFAULT_SEARCHING_KEY_ERROR = (
    'Ключ для поиска не может быть меньше, чем ключ, на основе которого была '
    'построена хеш-таблица в строгом режиме поиска!'
)

SEARCHING_KEY_SIZE_NOT_EQUAL_DEFAULT_SEARCHING_KEY_SIZE_ERROR = (
    'Длина ключа для поиска должна равняться длине ключа (searching_key), на основе которого была построена '
    'хеш-таблица в строгом режиме поиска!'
)

SEARCHING_KEY_NOT_EQUAL_DEFAULT_SEARCHING_KEY_ERROR = (
    'Поля ключа для поиска должны совпадать с полями ключа (searching_key), на основе которого была построена '
    'хеш-таблица в строгом режиме поиска!'
)

DATE_FROM_MORE_OR_EQUAL_DATE_TO_ERROR = 'Начальная дата должна быть строго меньше конечной даты'

NOT_SET_ONLY_AND_VALUES_FIELDS_ERROR = (
    'Пожалуйста, укажите список полей в only_fields или values_fields для ограничения выборки!'
)

SET_ONLY_AND_VALUES_FIELDS_ERROR = (
    'Должны быть указаны поля либо в only_fields, либо в values_fields. Одновременное указание запрещено!'
)

SEARCHING_FIELDS_IS_NOT_SUBSET_OF_ONLY_AND_VALUES_FIELDS = (
    'Поля в searching_fields должны входить в only_fields или value_fields! Ошибочные поля: {}.'
)

SPECIFIED_FIELD_NAME_INSTEAD_OF_ATTNAME_ERROR = (
    'При указании полей внешних ключей необходимо указывать имена с суффиксом _id! Ошибочное поле {}.'
)

SPECIFIED_FIELD_ATTNAME_INSTEAD_OF_NAME_ERROR = (
    'При указании цепочки полей внешних ключей, необходимо указывать имена (name) полей, а не attname! Полное имя '
    'поля {}, ошибочная часть {}.'
)

WRONG_RELATED_FIELD_NAME_ERROR = (
    'Ошибочное название поля внешней таблицы на текущую. В наименовании не должно быть _id. Если требуется обратиться '
    'к идентификатору, то нужно указывать __id. Полное имя поля {}, ошибочная часть {}.'
)

CAN_NOT_GET_RELATED_MODEL_VALUES_ERROR = (
    'Невозможно получить значение для обратной связи для модели. Необходимо указать конкретное поле! Полное имя '
    'поля {}, ошибочная часть {}.'
)

SPECIFIED_FIELDS_AFTER_PK_ERROR = (
    'После первичного ключа не могут быть указаны другие поля! Полное имя поля {}, ошибочная часть {}.'
)

FIELDS_NOT_FOUND_ERROR = 'Не удалось найти поля: {}'

FILTER_EQ_LOOKUP_VALUE_ITERABLE_ERROR = (
    'Значением фильтра __eq не может быть итерабельный объект! Поле - {}, значение - {}.'
)

FILTER_IN_LOOKUP_VALUE_NOT_ITERABLE_ERROR = (
    'Значением фильтра __in должен быть итерабельный объект! Поле - {}, значение - {}.'
)

FILTER_FIELD_NAME_NOT_IN_SEARCHING_FIELDS_ERROR = (
    'Фильтрация может быть осуществлена только по полям из searching_fields ({}). Найдена фильтрация по полю {}.'
)

FILTER_RANGE_LOOKUP_VALUE_NOT_CONTAIN_TWO_VALUES_ERROR = (
    'Значением фильтра _range должен быть итерабельный объект, состоящий из двух элементов. Первый элемент должен быть '
    'больше второго элемента. Поле - {}, значение - {}.'
)

FOUND_MORE_THAN_ONE_ENTITY_ERROR = 'Найдено больше одной записи!'

ENTITY_NOT_FOUND_ERROR = 'Не удалось найти записи!'

MULTIPLE_FIELDS_FOUND_IN_FLAT_MODE_ERROR = (
    'Обнаружено несколько полей в flat-режиме. Должно быть указано только одно поле!'
)

FIELDS_MUST_BE_FROM_ONLY_OR_VALUES_FIELDS_ERROR = (
    'Поля для получения значений должны быть только из only_fields или values_fields (). Найдено получение значений '
    'по полям - {}. '
)

FIELDS_NOT_PASSED_ERROR = 'Не указаны поля для выборки данных!'
