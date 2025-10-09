from collections import (
    defaultdict,
    namedtuple,
)
from copy import (
    deepcopy,
)
from datetime import (
    date,
)
from operator import (
    attrgetter,
)
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

from django.db.models import (
    Model,
    Q,
)

from m3_db_utils.consts import (
    LOOKUP_SEP,
    PK,
)

from function_tools.consts import (
    ALL,
)
from function_tools.enums import (
    LookupEnum,
    TransferPeriodEnum,
)
from function_tools.strings import (
    CAN_NOT_GET_RELATED_MODEL_VALUES_ERROR,
    DATE_FROM_MORE_OR_EQUAL_DATE_TO_ERROR,
    ENTITY_NOT_FOUND_ERROR,
    FIELDS_MUST_BE_FROM_ONLY_OR_VALUES_FIELDS_ERROR,
    FIELDS_NOT_FOUND_ERROR,
    FIELDS_NOT_PASSED_ERROR,
    FILTER_EQ_LOOKUP_VALUE_ITERABLE_ERROR,
    FILTER_FIELD_NAME_NOT_IN_SEARCHING_FIELDS_ERROR,
    FILTER_IN_LOOKUP_VALUE_NOT_ITERABLE_ERROR,
    FILTER_RANGE_LOOKUP_VALUE_NOT_CONTAIN_TWO_VALUES_ERROR,
    FOUND_MORE_THAN_ONE_ENTITY_ERROR,
    MULTIPLE_FIELDS_FOUND_IN_FLAT_MODE_ERROR,
    NOT_SET_ONLY_AND_VALUES_FIELDS_ERROR,
    SEARCHING_FIELDS_IS_NOT_SUBSET_OF_ONLY_AND_VALUES_FIELDS,
    SET_ONLY_AND_VALUES_FIELDS_ERROR,
    SPECIFIED_FIELD_ATTNAME_INSTEAD_OF_NAME_ERROR,
    SPECIFIED_FIELD_NAME_INSTEAD_OF_ATTNAME_ERROR,
    SPECIFIED_FIELDS_AFTER_PK_ERROR,
    WRONG_RELATED_FIELD_NAME_ERROR,
)
from function_tools.utils import (
    check_is_iterable,
    date2str,
    deep_getattr,
    find_gte,
    find_lte,
)


class BaseCache:
    """Кеш-заглушка."""

    def __init__(self, *args, **kwargs):
        super().__init__()

        # Кеш подготовлен к работе
        self.__is_prepared = False

    @property
    def is_prepared(self) -> bool:
        """Кеш уже подготовлен."""
        return self.__is_prepared

    @is_prepared.setter
    def is_prepared(self, value: bool):
        """Отметка кеша о готовности."""
        self.__is_prepared = value

    def _before_prepare(self, *args, **kwargs):
        """Действия перед подготовкой кеша."""

    def _prepare(self, *args, **kwargs):
        """Заполнение кеша данными."""

    def _after_prepare(self, *args, **kwargs):
        """Действия после подготовки кеша."""

    def _check_cache_prepared(self):
        """Проверка, был ли подготовлен кеш ранее или нет."""
        if self.is_prepared:
            raise RuntimeError('Cache can not be prepared twice. Please check using method "prepare".')

    def prepare(self, *args, **kwargs):
        """"""
        self._check_cache_prepared()

        self._before_prepare(*args, **kwargs)
        self._prepare(*args, **kwargs)
        self._after_prepare(*args, **kwargs)

        self.is_prepared = True


class EntityCache(BaseCache):
    """Базовый класс кеша объектов сущности.

    Не поддерживается работа с составными первичными ключами!

    В реализации приветствуется использование реального названия поля вместо pk. Это делается для унификации в работе
    механизмов поиска.

    В searching_fields указываются поля, по которым будет производиться поиск в кеше - методы get, filter. Если будет
    производиться поиск по полям, неуказанным в searching_fields будет падать ошибка. Ограничения связаны с построением
    только необходимых хеш-таблиц, по которым будет производиться поиск при работе с кешем. По умолчанию строится
    хеш-таблица для первичного ключа. Поля в searching_fields должны входить в only_fields или values_fields.

    Необходимо обратить внимание, что в only_fields нельзя передавать prefetch_related параметры, т.к. возникает ошибка.
    Вместо only_fields необходимо использовать values_fields.
    В приоритете использование only_fields, т.к. для values_fields требуется преобразование результата в виде словаря
    во вложенные объекты.
    """

    FILTER_FUNCTIONS = {
        'range': lambda r: lambda v: r[0] <= v <= r[1],
        'in': lambda r: lambda v: v in r,
        'eq': lambda r: lambda v: v == r,
    }

    def __init__(
        self,
        model: Type[Model],
        *args,
        select_related_fields: Optional[Tuple[str, ...]] = None,
        annotate_fields: Optional[Dict] = None,
        only_fields: Optional[Tuple[str, ...]] = None,
        values_fields: Optional[Tuple[str, ...]] = None,
        additional_filter_params: Optional[Union[Tuple[Union[Q, Dict[str, Any]]], Dict[str, Any]]] = None,
        exclude_params: Optional[Dict[str, Any]] = None,
        distinct: Optional[Union[bool, Tuple[str]]] = True,
        searching_fields: Tuple[str, ...] = ('pk',),
        is_force_fill_cache: bool = True,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._model = model
        self._model_pk_attname = self._model._meta.pk.attname
        self._annotate_fields = annotate_fields

        self._searching_fields = self._replace_pk_to_id(
            fields=searching_fields,
            is_add_id=True,
        )
        self._searching_rel_fields = set()
        self._initial_searching_hash_tables = defaultdict(dict)

        only_fields, values_fields = self._prepare_only_values_fields(
            only_fields=only_fields,
            values_fields=values_fields,
        )

        self._select_related_fields = select_related_fields

        self._only_fields = only_fields
        self._values_fields = values_fields

        self._check_searching_fields()

        self._searching_field_name_path_map = self._prepare_searching_field_name_path_map()

        self._actual_entities_queryset = self._prepare_actual_entities_queryset()

        self._additional_filter_params = (
            self._prepare_additional_filter_params(additional_filter_params) if additional_filter_params else ([], {})
        )
        self._exclude_params = exclude_params

        self._distinct = distinct

        self._is_force_fill_cache = is_force_fill_cache

        self._filters = {}
        self._is_filtered = False

        self._initial_entities = None
        self._initial_entities_qs = None

        self._filter_searching_hash_tables = {}

        if self._is_force_fill_cache:
            self.prepare(*args, **kwargs)

    def __repr__(self):
        return f'<{self.__class__.__name__} @model="{self._model.__name__}">'

    def __str__(self):
        return self.__repr__()

    def __iter__(self):
        """Обеспечивает итерирование по кешу.

        Например, когда была применена фильтрация filter() можно сразу итерироваться по полученному кешу."""
        entities = self.all()

        for entity in entities:
            yield entity

    @property
    def initial_entities_qs(self):
        """Возвращает начальный QuerySet, по которому делается выборка записей из БД без values."""
        return self._initial_entities_qs

    def _fill_all_fields(self, fields: Tuple[str]) -> Tuple[str]:
        """Добавляет в кортеж все поля модели."""
        tmp_fields = set(fields)

        tmp_fields.discard(ALL)

        tmp_fields.update([field.attname for field in self._model._meta.fields])

        tmp_fields.add(self._model_pk_attname)

        return tuple(tmp_fields)

    def _replace_pk_to_id(
        self,
        fields: Iterable[str],
        is_add_id: bool = False,
    ) -> Tuple[str]:
        """Производит замену pk на имя поля идентификатора модели.

        Args:
            fields: Список полей;
            is_add_id: Добавить в список полей идентификатор, если его не было ранее.
        """
        fields = list(fields)

        if PK in fields:
            fields = list(map(lambda x: x.replace(PK, self._model_pk_attname), fields))

        if is_add_id and self._model_pk_attname not in fields:
            fields.append(self._model_pk_attname)

        return tuple(fields)

    def _check_model_field(
        self,
        model: Type[Model],
        field_name_items: List[str],
        full_field_name: str,
    ):
        """Осуществляет рекурсивный поиск внешних ключей и проверяет, были указаны attname внешних ключей, а не name."""
        field_name_items_len = len(field_name_items)
        pk_attr_name = self._model._meta.pk.attname
        is_checked = False

        if field_name_items[0] == pk_attr_name:
            field_name_items.pop(0)

            self._searching_rel_fields.add(full_field_name)

            if field_name_items:
                raise ValueError(SPECIFIED_FIELDS_AFTER_PK_ERROR.format(full_field_name, field_name_items[0]))

        if field_name_items:
            for field in model._meta.fields:
                if field.name == field_name_items[0]:
                    if field.is_relation:
                        if field_name_items_len == 1:
                            raise ValueError(SPECIFIED_FIELD_NAME_INSTEAD_OF_ATTNAME_ERROR.format(full_field_name))
                        else:
                            field_name_items.pop(0)

                            self._check_model_field(
                                model=field.related_model,
                                field_name_items=field_name_items,
                                full_field_name=full_field_name,
                            )

                            is_checked = True
                            break
                    else:
                        field_name_items.pop(0)

                        is_checked = True
                        break
                elif field.attname == field_name_items[0]:
                    if field_name_items_len == 1:
                        field_name_items.pop()

                        self._searching_rel_fields.add(full_field_name)

                        is_checked = True
                        break
                    else:
                        raise ValueError(
                            SPECIFIED_FIELD_ATTNAME_INSTEAD_OF_NAME_ERROR.format(full_field_name, field_name_items[0])
                        )

        if field_name_items and not is_checked:
            for rel_field in model._meta.related_objects:
                if rel_field.name == field_name_items[0]:
                    if field_name_items_len == 1:
                        raise ValueError(
                            CAN_NOT_GET_RELATED_MODEL_VALUES_ERROR.format(full_field_name, field_name_items[0])
                        )
                    else:
                        field_name_items.pop(0)

                        self._check_model_field(
                            model=rel_field.related_model,
                            field_name_items=field_name_items,
                            full_field_name=full_field_name,
                        )

                        break
                elif f'{rel_field.name}_id' == field_name_items[0]:
                    raise ValueError(WRONG_RELATED_FIELD_NAME_ERROR.format(full_field_name, field_name_items[0]))

    def _check_model_fields(self, fields):
        """Проверяет, чтобы были указаны attname внешних ключей, а не name."""
        wrong_fields = []

        for field_name in fields:
            if self._annotate_fields and field_name in self._annotate_fields:
                continue

            fields_name_items = field_name.split(LOOKUP_SEP)

            self._check_model_field(
                model=self._model,
                field_name_items=fields_name_items,
                full_field_name=field_name,
            )

            if fields_name_items:
                wrong_fields.append(f'{field_name} - {LOOKUP_SEP.join(fields_name_items)}')

        if wrong_fields:
            raise ValueError(FIELDS_NOT_FOUND_ERROR.format(', '.join(wrong_fields)))

    def _prepare_only_values_fields(
        self,
        only_fields: Optional[Tuple[str]],
        values_fields: Optional[Tuple[str]],
    ) -> Tuple[Optional[Tuple[str]], Optional[Tuple[str]]]:
        """Подготавливает поля only и values к работе."""
        # Добавление всех полей модели, если указана *
        if only_fields and ALL in only_fields:
            only_fields = self._fill_all_fields(
                fields=only_fields,
            )
        elif values_fields and ALL in values_fields:
            values_fields = self._fill_all_fields(
                fields=values_fields,
            )

        # Замена pk на название поля идентификатора
        if only_fields:
            only_fields = self._replace_pk_to_id(
                fields=only_fields,
                is_add_id=True,
            )
        elif values_fields:
            values_fields = self._replace_pk_to_id(
                fields=values_fields,
                is_add_id=True,
            )

        if not (only_fields or values_fields):
            raise ValueError(NOT_SET_ONLY_AND_VALUES_FIELDS_ERROR)
        elif only_fields and values_fields:
            raise ValueError(SET_ONLY_AND_VALUES_FIELDS_ERROR)

        fields = only_fields or values_fields

        self._check_model_fields(
            fields=fields,
        )

        return only_fields, values_fields

    def _check_searching_fields(self):
        """Проверяет вхождение полей в only_fields или values_fields."""
        fields = self._only_fields or self._values_fields
        searching_fields = set(self._searching_fields)

        if not searching_fields.issubset(fields):
            diff_fields = searching_fields.difference(fields)

            raise ValueError(SEARCHING_FIELDS_IS_NOT_SUBSET_OF_ONLY_AND_VALUES_FIELDS.format(', '.join(diff_fields)))

    def _prepare_searching_field_name_path_map(self):
        """Формирует карту соответствия названия полей с путями получения атрибутов."""
        searching_field_name_path = {}

        for field_name in self._searching_fields:
            searching_field_name_path[field_name] = field_name.replace(LOOKUP_SEP, '.')

        return searching_field_name_path

    def _prepare_additional_filter_params(
        self,
        filter_params: Union[Tuple[Union[Q, Dict[str, Any]]], Dict[str, Any]],
    ) -> Tuple[List[Q], Dict[str, Any]]:
        """Подготовка параметров фильтрации.

        Args:
            filter_params: Параметры фильтрации задаваемые пользователем. Кортеж Q со словарем для именованных
                параметров, например, обозначение вхождения.
        """
        filter_args = []
        filter_kwargs = {}

        if isinstance(filter_params, dict):
            filter_kwargs = filter_params
        else:
            for param in filter_params:
                if isinstance(param, Q):
                    filter_args.append(param)
                elif isinstance(param, dict):
                    filter_kwargs.update(**param)
                else:
                    raise ValueError('Please, check `additional_filter_params`, incorrect value!')

        return filter_args, filter_kwargs

    def _before_prepare(self, *args, **kwargs):
        """Точка расширения перед подготовкой кеша."""
        pass

    def _after_prepare(self, *args, **kwargs):
        """Точка расширения после подготовки кеша."""
        pass

    def _prepare(self, *args, **kwargs):
        """Метод подготовки кеша."""
        self._prepare_entities()
        self._prepare_entity_hash_tables()

    def _prepare_entities(self):
        """Получение выборки объектов модели по указанными параметрам."""
        self._initial_entities = self._actual_entities_queryset

        if self._annotate_fields:
            self._initial_entities = self._initial_entities.annotate(**self._annotate_fields)

        if self._additional_filter_params[0]:
            self._initial_entities = self._initial_entities.filter(*self._additional_filter_params[0])

        if self._additional_filter_params[1]:
            self._initial_entities = self._initial_entities.filter(**self._additional_filter_params[1])

        if self._exclude_params:
            self._initial_entities = self._initial_entities.exclude(**self._exclude_params)

        if self._only_fields:
            self._initial_entities = self._initial_entities.only(*self._only_fields)

        if self._distinct:
            if isinstance(self._distinct, Iterable):
                self._initial_entities = self._initial_entities.distinct(*self._distinct)
            else:
                self._initial_entities = self._initial_entities.distinct()

        self._initial_entities_qs = self._initial_entities

        if self._values_fields:
            self._initial_entities = self._initial_entities.values(*self._values_fields)

        if self._values_fields:
            self._convert_values_to_objects()

    def _build_object_classes(self, field_structure, field_name: str):
        """Формирует классы именованных кортежей для вложенных объектов."""
        if field_structure.get('fields'):
            name = f'{field_name.capitalize()}NamedTuple'

            entity_cls = namedtuple(name, field_structure['fields'].keys())

            field_structure['cls'] = entity_cls

            for field_name, field_value in field_structure['fields'].items():
                if field_value:
                    self._build_object_classes(
                        field_structure=field_value,
                        field_name=field_name,
                    )
        else:
            field_structure['cls'] = None

    def _prepare_field_structure(self) -> Dict[str, Dict[str, Dict]]:
        """Формирование структуры объектов и их полей в виде словаря."""
        field_structure = defaultdict(dict)

        for field in self._values_fields:
            field_items = field.split(LOOKUP_SEP)
            tmp_level = field_structure

            for field_item in field_items:
                if field_item not in tmp_level['fields']:
                    tmp_level['fields'][field_item] = defaultdict(dict)

                tmp_level = tmp_level['fields'][field_item]

        self._build_object_classes(
            field_structure=field_structure,
            field_name=self._model.__class__.__name__,
        )

        return field_structure

    def _build_entity_object(self, entity, field_structure, field_path=()):
        """Формирование объекта сущности из словаря."""
        field_values = {}

        for field_key, field_value in field_structure['fields'].items():
            if field_value:
                value = self._build_entity_object(
                    entity=entity,
                    field_structure=field_value,
                    field_path=(field_path + (field_key,)),
                )
            else:
                tmp_field_key = field_key

                if field_key == PK:
                    tmp_field_key = self._model._meta.pk.name

                tmp_field_key = f'{LOOKUP_SEP}'.join((field_path + (tmp_field_key,)))

                value = entity.get(tmp_field_key)

            field_values[field_key] = value

        entity_object = field_structure['cls'](**field_values)

        return entity_object

    def _convert_values_to_objects(self):
        """Преобразование словарей, полученных при помощи values() в структуру объектов для работы как с обычными QS."""
        field_structure = self._prepare_field_structure()

        tmp_entities = []

        for entity in self._initial_entities:
            entity_object = self._build_entity_object(
                entity=entity,
                field_structure=field_structure,
            )

            tmp_entities.append(entity_object)

        del self._initial_entities

        self._initial_entities = tmp_entities

    def _prepare_entities_hash_table(self):
        """Отвечает за построение хеш таблицы для дальнейшего поиска.

        В качестве ключа можно задавать строку - наименование поля или кортеж наименований полей.

        Если требуется доступ через внешний ключ, то необходимо использовать точку в качестве разделителей. Например,
        searching_key = tuple('account_id', 'supplier.code').
        """
        hash_table = {}

        key_items_count = len(self._searching_key)
        for entity in self._initial_entities:
            temp_hash_item = hash_table

            for index, key_item in enumerate(self._searching_key, start=1):
                key_item_value = deep_getattr(entity, key_item)

                if key_item_value is not None:
                    if index == key_items_count:
                        if key_item_value not in temp_hash_item:
                            temp_hash_item[key_item_value] = entity
                        else:
                            if isinstance(temp_hash_item[key_item_value], set):
                                temp_hash_item[key_item_value].add(entity)
                            else:
                                temp_hash_item[key_item_value] = {temp_hash_item[key_item_value], entity}
                    else:
                        if key_item_value not in temp_hash_item:
                            temp_hash_item[key_item_value] = {}

                        temp_hash_item = temp_hash_item[key_item_value]
                else:
                    break

        self._initial_entities_hash_table = hash_table

    def _sort_searching_hash_table_keys(self):
        """Производится сортировка ключей хеш-таблиц сформированных по полям searching_fields.

        Поля не являются внешними и первичным ключами."""
        not_rel_searching_fields = set(self._searching_fields).difference(self._searching_rel_fields)

        for field_name in not_rel_searching_fields:
            hash_table = self._initial_searching_hash_tables[field_name]

            unsorted_keys = list(hash_table.keys())
            sorted_keys = sorted(unsorted_keys, key=lambda x: (x is None, x))

            sorted_hash_table = {key: hash_table[key] for key in sorted_keys}

            self._initial_searching_hash_tables[field_name] = sorted_hash_table

            del hash_table

    def _prepare_entity_hash_tables(self):
        """Формирование хеш-таблиц для всех полей.

        Для каждого поля из searching_fields формируется отдельная хеш-таблица, где в качестве ключей выступают
        значения полей, а в качестве значений множества с идентификаторами записей. Исключением является хеш-таблица,
        где значениями являются не идентификаторы, а сами сущности.

        Если название поля входят в _searching_rel_fields, где хранятся внешние и первичный ключи, то ключи не должны
        быть отсортированы. В остальных случаях, ключи хеш-таблиц должны быть отсортированы по возрастанию. Это
        позволит осуществлять поиск границ при использовании фильтров range, (lt, lte, gt, gte - еще не реализованы).
        """
        searching_fields_names = list(self._searching_field_name_path_map.keys())

        pk_field_index = searching_fields_names.index(self._model_pk_attname)

        searching_fields_paths = list(self._searching_field_name_path_map.values())
        searching_fields_attrgetter = attrgetter(*searching_fields_paths)

        for entity in self._initial_entities:
            searching_field_values = searching_fields_attrgetter(entity)

            # Если в searching_fields будет только одно поле, то attrgetter вернет не кортеж, а одиночное значение
            searching_field_values = (
                searching_field_values if check_is_iterable(searching_field_values) else (searching_field_values,)
            )

            pk_field_value = searching_field_values[pk_field_index]

            self._initial_searching_hash_tables[self._model_pk_attname][pk_field_value] = entity

            for index, field_name in enumerate(searching_fields_names):
                if field_name == self._model_pk_attname:
                    continue

                field_value = searching_field_values[index]

                if field_value not in self._initial_searching_hash_tables[field_name]:
                    self._initial_searching_hash_tables[field_name][field_value] = set()

                self._initial_searching_hash_tables[field_name][field_value].add(pk_field_value)

        self._sort_searching_hash_table_keys()

    def _prepare_actual_entities_queryset(self):
        """Подготовка менеджера с указанием идентификатора учреждения и состояния, если такие имеются у модели."""
        actual_entities_queryset = self._model._base_manager.all()

        return actual_entities_queryset

    def _filter_eq(
        self,
        field_name: str,
        value: Any,
        searching_hash_table: Dict[str, Set[Any]],
    ) -> Optional[Dict[str, Set[Any]]]:
        """Осуществляет фильтрацию по указанному полю и значению.

        По указанному полю в хеш-таблице отфильтрованных значений осуществляется дополнительная фильтрация. Если
        хеш-таблица отфильтрованных значений еще не существует, то она формируется из начальной хеш-таблицы.

        Args:
            field_name: Название поля;
            value: Значение, которому должно соответствовать значение поля;
            searching_hash_table: хеш-таблица поля для поиска.
        """
        if check_is_iterable(value):
            raise ValueError(FILTER_EQ_LOOKUP_VALUE_ITERABLE_ERROR.format(field_name, value))

        new_searching_hash_table = self._filter_in(
            field_name=field_name,
            value=(value,),
            searching_hash_table=searching_hash_table,
        )

        return new_searching_hash_table

    def _filter_in(
        self,
        field_name: str,
        value: Any,
        searching_hash_table: Dict[str, Set[Any]],
    ) -> Optional[Dict[str, Set[Any]]]:
        """Осуществляет фильтрацию по указанному полю по принципу вхождения в указанный итерабельный объект.

        По указанному полю в хеш-таблице отфильтрованных значений осуществляется дополнительная фильтрация. Если
        хеш-таблица отфильтрованных значений еще не существует, то она формируется из начальной хеш-таблицы.

        Args:
            field_name: Название поля;
            value: Перечисление значений, в которые должно попадать значение поля;
            searching_hash_table: хеш-таблица поля для поиска.
        """
        if not check_is_iterable(value):
            raise ValueError(FILTER_IN_LOOKUP_VALUE_NOT_ITERABLE_ERROR(field_name, value))

        if field_name not in self._searching_rel_fields:
            value = sorted(value)

        tmp_hash_table = {v: searching_hash_table[v] for v in value if v in searching_hash_table}

        return tmp_hash_table

    def _filter_range(
        self,
        field_name: str,
        value: Tuple[Any, Any],
        searching_hash_table: Dict[str, Set[Any]],
    ) -> Optional[Dict[str, Set[Any]]]:
        """Осуществляет фильтрацию по указанному полю в переданном диапазоне значений.

        По указанному полю в хеш-таблице отфильтрованных значений осуществляется дополнительная фильтрация. Если
        хеш-таблица отфильтрованных значений еще не существует, то она формируется из начальной хеш-таблицы.

        Принцип работы заключается в выявлении граничных значений ключей хеш-таблицы. Т.к. ключи отсортированы по
        возрастанию, то при нахождении граничных значений и их индексов ключей, выбирается
        """
        if not check_is_iterable(value) or len(value) != 2 or value[0] > value[1]:
            raise ValueError(FILTER_RANGE_LOOKUP_VALUE_NOT_CONTAIN_TWO_VALUES_ERROR.format(field_name, value))

        # None будет только в том случае, если границы значений не будут уточнены
        new_searching_hash_table = None

        # Если передали одинаковые значения, то отфильтруем как равенство
        if value[0] == value[1]:
            new_searching_hash_table = self._filter_eq(
                field_name=field_name,
                value=value[0],
                searching_hash_table=searching_hash_table,
            )
        else:
            field_values = list(searching_hash_table.keys())

            left_boundary_value_index, _ = find_gte(
                iterable_object=field_values,
                target_value=value[0],
            )

            right_boundary_value_index, _ = find_lte(
                iterable_object=field_values,
                target_value=value[1],
            )

            # Если границы не удалось определить, то значения не могут быть найдены
            if left_boundary_value_index is None or right_boundary_value_index is None:
                new_searching_hash_table = {}
            # Если границы не совпадают с размерностью набора ключей, то требуется уточнение
            elif left_boundary_value_index != 0 or right_boundary_value_index != len(field_values) - 1:
                sliced_field_values = field_values[left_boundary_value_index : right_boundary_value_index + 1]

                new_searching_hash_table = {
                    field_value: searching_hash_table[field_value] for field_value in sliced_field_values
                }

        return new_searching_hash_table

    def _apply_filter_to_searching_hash_tables(
        self,
        searching_hash_tables: Dict[str, Dict[str, Any]],
        **kwargs,
    ):
        """Применение фильтров к хеш-таблицам полей для поиска."""
        for attr, value_filter in kwargs.items():
            lookup_attr = attr.split(LOOKUP_SEP)

            if len(lookup_attr) == 1:
                lookup = LookupEnum.EQ
                field_name = lookup_attr[0]
            else:
                lookup = LookupEnum(lookup_attr[-1])
                field_name = LOOKUP_SEP.join(lookup_attr[:-1])

            if field_name == PK:
                field_name = self._model_pk_attname
            elif field_name not in self._searching_fields:
                raise ValueError(
                    FILTER_FIELD_NAME_NOT_IN_SEARCHING_FIELDS_ERROR.format(
                        ', '.join(self._searching_fields), field_name
                    )
                )

            filter_function = getattr(self, f'_filter_{lookup.value}')

            searching_hash_table = (
                searching_hash_tables[field_name]
                if field_name in searching_hash_tables
                else self._initial_searching_hash_tables[field_name]
            )

            new_searching_hash_table = filter_function(
                field_name=field_name,
                value=value_filter,
                searching_hash_table=searching_hash_table,
            )

            if new_searching_hash_table is not None:
                searching_hash_tables[field_name] = new_searching_hash_table

    def _get_entities_by_searching_hash_tables(
        self,
        searching_hash_tables: Dict[str, Dict[str, Any]],
    ) -> Union[List[NamedTuple], List[Model]]:
        """Получение сущностей исходя из хеш-таблиц полей для поиска."""
        field_entity_ids = defaultdict(set)

        for field_name in searching_hash_tables:
            if field_name == self._model_pk_attname:
                field_entity_ids[field_name].update(searching_hash_tables[field_name])

                continue

            # Если в хеш таблице по полю нет значений, значит по одному из фильтров не были найдены
            # соответствующие условию значения
            if not searching_hash_tables[field_name]:
                field_entity_ids[field_name] = set()
                break

            for field_value in searching_hash_tables[field_name]:
                field_entity_ids[field_name].update(searching_hash_tables[field_name][field_value])

        entity_ids = set.intersection(*field_entity_ids.values())

        entities = [self._initial_searching_hash_tables[self._model_pk_attname][entity_id] for entity_id in entity_ids]

        return entities

    def all(self) -> Union[List[NamedTuple], List[Model]]:
        """Возвращает список именованных кортежей либо QuerySet в зависимости от подхода к получению объектов."""
        if self._filter_searching_hash_tables:
            entities = self._get_entities_by_searching_hash_tables(
                searching_hash_tables=self._filter_searching_hash_tables,
            )
        else:
            entities = list(self._initial_searching_hash_tables[self._model_pk_attname].values())

        return entities

    def clear_filter(self):
        """Сброс примененных фильтров."""
        del self._filter_searching_hash_tables

        self._filter_searching_hash_tables = defaultdict(dict)

    def filter(
        self,
        refresh_filter: bool = True,
        **kwargs,
    ):
        """Фильтрация данных кеша для дальнейшего их получения.

         В фильтрации могут участвовать поля из searching_fields. Если будут встречаться отличные поля, будет вызвано
         исключение.

         Если в названии поля используется двойное подчеркивание __, то обязательно нужно указывать правило фильтрации,
         например, __eq.

         Каждый фильтр рассматривается отдельно. Полученные по нему значения заносятся в `_filter_searching_hash_tables`,
         где для каждого поля создается своя хеш-таблица. При дальнейшей выборке данных производится работа с
        ` _filter_searching_hash_tables`, если ранее была осуществлена фильтрация и не было принудительной зачистки
         фильтра при помощи метода `clear_filter`.

         Предусмотрены несколько вариантов работы:
             - В обычном режиме, при запуске новой фильтрации, предыдущий результат фильтрации стирается и производится
                 фильтрация исходных данных (`refresh_filter=True`). Это тот случай, когда требуется обнуление фильтров.
                 Режим по умолчанию;
             - Для формирования цепочки фильтров можно указывать параметр `refresh_filter=False`. В этом случае фильтры
                 будут работать в режиме уточнения. Ранее отфильтрованные значения будут дополнительно отфильтрованы
                 согласно новых условий.

         Пример использования:
         some_objects_list = cache.filter(
             id__range=(1,10),
             elements_id__in=[1,2,3],
         ).values_list('id')
         some_objects_list => [1,5,6]

         some_objects_list = cache.filter(
             id__range=(1,10),
             elements_id__in=[1,2,3],
         ).values_list('id', 'elements_id')
         some_objects_list => [(1,1), (5,2), (6,3)]

         Args:
             refresh_filter: отвечает за очистку фильтра для работы с данными в исходном состоянии.
        """
        if refresh_filter:
            self.clear_filter()

        self._apply_filter_to_searching_hash_tables(
            searching_hash_tables=self._filter_searching_hash_tables,
            **kwargs,
        )

        return self

    def get(
        self,
        silent_mode: bool = True,
        refresh_filter: bool = True,
        **kwargs,
    ):
        """Метод получения записи из кеша.

        В фильтрации могут участвовать поля из searching_fields. Если будут встречаться отличные поля, будет вызвано
        исключение.

        Каждый фильтр рассматривается отдельно. Изначально временные хеш-таблицы полей tmp_filter_searching_hash_tables
        формируются на основе хеш-таблиц полей _filter_searching_hash_tables, если ранее были применены фильтры и не
        было принудительной зачистки фильтра при помощи метода `clear_filter`. Полученные по фильтру значения заносятся
        в `tmp_filter_searching_hash_tables`, где производится уточнение фильтров, если ранее была фильтрация по
        указанным полям.

        Предусмотрен "тихий" режим работы выбранный по умолчанию, когда при отсутствии записей или выборе множества
        записей не выпадает исключение и возвращается None.

        Пример использования:
        some_object = cache.get(
            id__range=(1,10),
            elements_id__in=[1,2,3],
        )
        some_object => object

        some_object = cache.filter(
            id__range=(1,10),
            elements_id__in=[1,2,3],
        ).get(
            date__range=(
                date(2014, 1, 1),
                date(2015, 12, 31),
            ),
        )
        some_object => None

        some_object = cache.filter(
            id__range=(1,10),
            elements_id__in=[1,2,3],
        ).get(
            date__range=(
                date(2014, 1, 1),
                date(2015, 12, 31),
            ),
            silent_mode=False,
        )
        some_object => raise RuntimeError

        Args:
            silent_mode: Включен "тихий" режим работы;
            refresh_filter: Очистить ранее примененные фильтры.
        """
        if refresh_filter:
            self.clear_filter()

        tmp_filter_searching_hash_tables = (
            deepcopy(self._filter_searching_hash_tables) if self._filter_searching_hash_tables else {}
        )

        self._apply_filter_to_searching_hash_tables(
            searching_hash_tables=tmp_filter_searching_hash_tables,
            **kwargs,
        )

        if tmp_filter_searching_hash_tables:
            entities = self._get_entities_by_searching_hash_tables(
                searching_hash_tables=tmp_filter_searching_hash_tables,
            )
        else:
            entities = list(self._initial_searching_hash_tables[self._model_pk_attname].values())

        entities_len = len(entities)

        if entities_len > 1:
            if not silent_mode:
                raise RuntimeError(FOUND_MORE_THAN_ONE_ENTITY_ERROR)

            entity_item = None
        elif entities_len == 0:
            if not silent_mode:
                raise RuntimeError(ENTITY_NOT_FOUND_ERROR)

            entity_item = None
        else:
            entity_item = entities[0]

        return entity_item

    def first(self):
        """Получение первого элемента из кеша.

        Если ранее была наложена фильтрация, то значение будет получено из отфильтрованной выборки.
        """
        entities = self.all()

        first_entity = entities[0] if entities else None

        return first_entity

    def last(self):
        """Получение последнего элемента из кеша.

        Если ранее была наложена фильтрация, то значение будет получено из отфильтрованной выборки.
        """
        entities = self.all()

        first_entity = entities[-1] if entities else None

        return first_entity

    def exists(self) -> bool:
        """Проверка существования отфильтрованных данных."""
        entities = self.all()

        return bool(entities)

    def values_list(
        self,
        *args,
        flat: bool = False,
    ) -> Optional[List[List]]:
        """Получение списка кортежей состоящих из значений полей объектов согласно заданным параметрам."""
        if not args:
            raise ValueError(FIELDS_NOT_PASSED_ERROR)

        entities = self.all()

        if flat and len(args) > 1:
            raise RuntimeError(MULTIPLE_FIELDS_FOUND_IN_FLAT_MODE_ERROR)

        args = self._replace_pk_to_id(
            fields=args,
        )

        fields = self._only_fields or self._values_fields

        if not set(args).issubset(fields):
            diff_fields = set(fields).difference(args)

            raise RuntimeError(
                FIELDS_MUST_BE_FROM_ONLY_OR_VALUES_FIELDS_ERROR.format(
                    ', '.join(diff_fields),
                )
            )

        values_fields = [p.replace(LOOKUP_SEP, '.') for p in args]

        fields_getter = attrgetter(*values_fields)

        values_list_ = [fields_getter(entity) for entity in entities]

        if flat:
            values_list_ = list(filter(None, set(values_list_)))

        return values_list_

    def values(
        self,
        *args,
    ) -> List[Dict[str, Any]]:
        """Получение списка словарей сформированных из сущностей по указанным полям.

        Необходимо обратить внимание, что `pk` заменяется на атрибут первичного ключа модели.
        """
        if not args:
            raise ValueError(FIELDS_NOT_PASSED_ERROR)

        entities = self.all()

        args = self._replace_pk_to_id(
            fields=args,
        )

        fields = self._only_fields or self._values_fields

        if not set(args).issubset(fields):
            diff_fields = set(fields).difference(args)

            raise RuntimeError(
                FIELDS_MUST_BE_FROM_ONLY_OR_VALUES_FIELDS_ERROR.format(
                    ', '.join(diff_fields),
                )
            )

        values_fields = [p.replace(LOOKUP_SEP, '.') for p in args]

        fields_getter = attrgetter(*values_fields)

        values_list_ = [fields_getter(entity) for entity in entities]

        values = [dict(zip(args, entity)) for entity in values_list_]

        return values


class ActualEntityCache(EntityCache):
    """Базовый класс кеша актуальных записей сущности."""

    def __init__(
        self,
        actual_date,
        *args,
        **kwargs,
    ):
        self._actual_date = actual_date

        super().__init__(*args, **kwargs)

    def _prepare_actual_entities_queryset(self) -> Dict[str, date]:
        """Метод получения фильтра актуализации по дате."""
        actual_entities_queryset = super()._prepare_actual_entities_queryset()

        actual_entities_queryset = actual_entities_queryset.filter(
            begin__lte=self._actual_date,
            end__gte=self._actual_date,
        )

        return actual_entities_queryset


class PeriodicalEntityCache(BaseCache):
    """Базовый класс периодического кеша.

    Кеш создается для определенной модели с указанием двух дат, на которые
    должны быть собраны кеши актуальных объектов модели.

    Для примера, может использоваться при переносах остатков на очередной год
    с 31 декабря на 1 января нового года.
    """

    entity_cache_class = EntityCache

    def __init__(
        self,
        date_from: date,
        date_to: date,
        model: Type[Model],
        *args,
        select_related_fields: Optional[Tuple[str, ...]] = None,
        annotate_fields: Optional[Dict] = None,
        only_fields: Optional[Tuple[str, ...]] = None,
        values_fields: Optional[Tuple[str, ...]] = None,
        additional_filter_params: Optional[Union[Tuple[Union[Q, Dict[str, Any]]], Dict[str, Any]]] = None,
        exclude_params: Optional[Dict[str, Any]] = None,
        searching_key: Union[str, Tuple[str, ...]] = ('pk',),
        is_force_fill_cache: bool = True,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        if date_from >= date_to:
            raise ValueError(DATE_FROM_MORE_OR_EQUAL_DATE_TO_ERROR)

        self._model = model
        self._select_related_fields = select_related_fields
        self._annotate_fields = annotate_fields
        self._only_fields = only_fields
        self._values_fields = values_fields

        self._additional_filter_params = (
            self._prepare_additional_filter_params(additional_filter_params) if additional_filter_params else ([], {})
        )

        self._exclude_params = exclude_params

        self._is_force_fill_cache = is_force_fill_cache

        self._searching_key = searching_key

        self._date_from = date_from
        self._date_to = date_to

        self._old_entities_cache: Optional[EntityCache] = None
        self._new_entities_cache: Optional[EntityCache] = None

        if self._is_force_fill_cache:
            self.prepare(*args, **kwargs)

    def __repr__(self):
        return (
            f'<{self.__class__.__name__} @model="{self._model.__name__}" '
            f'@date_from="{date2str(self._date_from)}" '
            f'@date_to="{date2str(self._date_to)}" '
            f'@searching_key="{self._searching_key}">'
        )

    def __str__(self):
        return self.__repr__()

    @property
    def old(self):
        """Кеш объектов модели актуальных на начальную дату."""
        return self._old_entities_cache

    @property
    def new(self):
        """Кеш объектов модели актуальный на конечную дату."""
        return self._new_entities_cache

    def _prepare_additional_filter_params(
        self,
        filter_params: Union[Tuple[Union[Q, Dict[str, Any]]], Dict[str, Any]],
    ) -> Tuple[List[Q], Dict[str, Any]]:
        """Подготовка параметров фильтрации.

        Args:
            filter_params: Параметры фильтрации задаваемые пользователем. Кортеж Q со словарем для именованных
                параметров, например, обозначение вхождения.
        """
        filter_args = []
        filter_kwargs = {}

        if isinstance(filter_params, dict):
            filter_kwargs = filter_params
        else:
            for param in filter_params:
                if isinstance(param, Q):
                    filter_args.append(param)
                elif isinstance(param, dict):
                    filter_kwargs.update(**param)
                else:
                    raise ValueError('Please, check `additional_filter_params`, incorrect value!')

        return filter_args, filter_kwargs

    def _get_actuality_filter(
        self,
        period_type: str,
    ) -> Dict[str, date]:
        """
        Метод получения фильтра актуализации по дате.

        При получении счетов или аналитик при переносе остатков необходимо
        учитывать период действия следуя следующей логике:
        -- старые - begin < date_from &&  end >= date_from
        -- новые - begin <= date_to && end > date_to

        :param dict period_type: словарь с параметрами для актуализации по дате
        :return:
        """
        if period_type == TransferPeriodEnum.OLD:
            actuality_filter = {
                'begin__lt': self._date_from,
                'end__gte': self._date_from,
            }
        else:
            actuality_filter = {
                'begin__lte': self._date_to,
                'end__gt': self._date_to,
            }

        return actuality_filter

    def _prepare_entities_cache(
        self,
        additional_filter_params: Tuple[Union[Q, Dict[str, Any]]],
    ):
        """Создание кеша объектов модели на указанную дату по указанным параметрам.

        С ключом поиска производится построения хеш-таблицы.
        """
        entities_cache = self.entity_cache_class(
            model=self._model,
            select_related_fields=self._select_related_fields,
            annotate_fields=self._annotate_fields,
            only_fields=self._only_fields,
            values_fields=self._values_fields,
            additional_filter_params=additional_filter_params,
            exclude_params=self._exclude_params,
            searching_key=self._searching_key,
            is_force_fill_cache=self._is_force_fill_cache,
        )

        return entities_cache

    def _prepare_periodical_additional_filter_params(
        self,
        period_type: str,
    ) -> Tuple[Union[Q, Dict[str, Any]]]:
        """Подготовка словаря с дополнительными параметрами для дальнейшей фильтрации объектов при формировании кеша."""
        additional_filter_params = deepcopy(self._additional_filter_params)

        additional_filter_params[1].update(
            **self._get_actuality_filter(
                period_type=period_type,
            )
        )

        return (*additional_filter_params[0], additional_filter_params[1])

    def _prepare_old_additional_filter_params(self):
        """Подготовка дополнительных параметров фильтрации на начальную дату."""
        return self._prepare_periodical_additional_filter_params(
            period_type=TransferPeriodEnum.OLD,
        )

    def _prepare_new_additional_filter_params(self):
        """Подготовка дополнительных параметров фильтрации на конечную дату."""
        return self._prepare_periodical_additional_filter_params(
            period_type=TransferPeriodEnum.NEW,
        )

    def _prepare_old_entities_cache(self):
        """Формирование кеша объектов модели на начальную дату."""
        additional_filter_params = self._prepare_old_additional_filter_params()

        self._old_entities_cache = self._prepare_entities_cache(
            additional_filter_params=additional_filter_params,
        )

    def _prepare_new_entities_cache(self):
        """Формирование кеша объектов модели на конечную дату."""
        additional_filter_params = self._prepare_new_additional_filter_params()

        self._new_entities_cache = self._prepare_entities_cache(
            additional_filter_params=additional_filter_params,
        )

    def _before_prepare(self, *args, **kwargs):
        """Точка расширения перед формированием кеша."""

    def _prepare(self, *args, **kwargs):
        """Формирование кешей на начальную и конечную даты."""
        self._prepare_old_entities_cache()
        self._prepare_new_entities_cache()

    def _after_prepare(self, *args, **kwargs):
        """Точка расширения после формирования кеша."""


class CacheStorage(BaseCache):
    """Хранилище кешей.

    Для выполнения функций, в большинстве случаев, необходимы кеши для
    множества сущностей созданные по особым правилам, но подчиняющиеся общим.
    Для их объединения и применения в функции создаются хранилища, содержащие кеши в виде публичных свойств, с
    которыми в дальнейшем удобно работать
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def prepare(self, *args, **kwargs):
        """Подготовка хранилища кешей.

        При подготовке хранилища должна быть произведена подготовка всех кешей для работы с ними.
        """
        super().prepare(*args, **kwargs)

        for attr_value in self.__dict__.values():
            if isinstance(attr_value, BaseCache) and not attr_value.is_prepared:
                attr_value.prepare(*args, **kwargs)


class PatchedGlobalCacheStorage(CacheStorage):
    """Хранилище кешей.

    Дополнен функциональностью патчинга кеша или хранилища кешей с использованием глобального (внешнего)
    кеша или хранилища кешей. Пригождается в случае использования глобального хелпера, когда есть необходимость
    создания кеша функции на основе кеша ранера.
    """

    def patch_by_global_cache(
        self,
        global_cache: BaseCache,
    ):
        """Патчинг кеша или хранилища кеша с использованием внешнего кеша или хранилища кешей.

        Args:
            global_cache: Внешний кеш или хранилище кешей.
        """
        pass
