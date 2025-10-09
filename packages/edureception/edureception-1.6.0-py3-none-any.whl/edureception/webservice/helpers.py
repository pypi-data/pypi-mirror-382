# coding:utf-8
from __future__ import (
    absolute_import,
    unicode_literals,
)

from django.db.models import (
    Model,
    fields,
)
from django.utils.translation import (
    gettext as _,
)
from future.builtins import (
    object,
    str,
)
from future.utils import (
    iteritems,
)
from m3.db import (
    BaseEnumerate,
)

from educommon import (
    ioc,
)
from m3_django_compatibility import (
    ModelOptions,
)

from ..base import (
    ReferenceProxy,
    ReferenceVirtualModelProxy,
)
from ..models import (
    ReasonsProxy,
)
from . import (
    entities,
)
from .errors import (
    EdureceptionServiceError,
    EdureceptionTypeError,
)


TimeTableRecord = ioc.get('edureception__TimeTableRecord')
ApplicantReception = ioc.get('edureception__ApplicantReception')


ABSENT_VALUE_STRING = _('Отсутствует')

# Вернуть значение в виде дерева
TREE_DATA = 'SUBTREE'
# Вернуть значение одного уровня
ONE_LEVEL_DATA = 'ONELEVEL'

# "P" модель плоская(не иерархичная) / "H" иерархичная
ONE_LEVEL_MODEL = 'P'
TREE_MODEL = 'H'


class ResponseStatusEnum(object):
    """Возможные статусы ответа на запрос"""

    SUCCESS = 0
    INTERNAL_ERROR = 1
    INPUT_ERROR = 2
    UNABLE_PERFORM_REQUEST = 4
    UNSUPPORTED_USER = 6

    values = {
        SUCCESS: _('ОК'),
        INTERNAL_ERROR: _('Внутренняя ошибка системы'),
        INPUT_ERROR: _('Ошибка во входных параметрах'),
        UNABLE_PERFORM_REQUEST: _(
            'Невозможно завершить процедуру бронирования в связи с тем, что указанный слот уже занят'
        ),
        UNSUPPORTED_USER: _('Услуга предоставляется только пользователям с подтвержденной учетной записью ЕСИА'),
    }

    @classmethod
    def get_choices(cls):
        """
        Используется для ограничения полей ORM и в качестве источника данных
        в ArrayStore и DataStore ExtJS
        """
        return list(iteritems(cls.values))

    get_items = get_choices

    @classmethod
    def get_constant_value_by_name(cls, name):
        """
        Возвращает значение атрибута константы, которая используется в
        качестве ключа к словарю values
        """
        if not isinstance(name, (str, bytes)):
            raise TypeError("'name' must be a string")

        if not name:
            raise ValueError("'name' must not be empty")

        return cls.__dict__[name]


class RefsListEnum(object):
    """
    Класс преднозначен для работы с справочниками:
    Учреждение,
    Причина записи на прием,
    Типы документов удостоверяющих личность

    Пример данных о справочнике
    values = {
        ORGANIZATIONS: {
            "model": Territory, Модель
            "title": "Инспекция", Название модели
            "kind": "P", "P" модель плоская(не иерархичная) / "H" иерархичная
            "self_reference_field": "", имя атрибута сслыающегося на себя
            "fields": [
                {
                    "name": "code",
                    "title": "Код",
                    "type": "STRING",
                    "attrRefName": "",  Всегда пусто
                    "allowFiltering": True  Всегда True
                }
                ....
            ]
        },
        ...
    }

    """

    ORGANIZATIONS = 'Organizations'
    REASONS = 'Reasons'
    IDENTITY_DOCUMENTS_TYPES = 'IdentityDocumentsTypes'

    values = {}

    # взаимосвязь модели с строковым обозначением
    relationship = {}

    # ассоциации типов полей модели к параметрам запроса
    type_fields = {
        fields.CharField: 'STRING',
        fields.BooleanField: 'BOOLEAN',
        fields.DecimalField: 'DECIMAL',
        fields.DateTimeField: 'DATETIME',
        fields.IntegerField: 'LONG',
        fields.AutoField: 'LONG',
    }

    def __init__(self):
        """
        Инициализируем данные справочников используя ioc
        :return: Заполняем массив данных с необходимой информацией для сервисов
        """
        organizations = ioc.get('edureception__Organizations')
        reasons = ReasonsProxy
        identity_documents_types = ioc.get('edureception__IdentityDocumentsTypes')
        self.relationship = {
            self.ORGANIZATIONS: organizations,
            self.REASONS: reasons,
            self.IDENTITY_DOCUMENTS_TYPES: identity_documents_types,
        }

        for key in self.relationship:
            reference_proxy = self.relationship[key]
            if not issubclass(reference_proxy.model, (Model, BaseEnumerate)):
                raise EdureceptionTypeError(
                    'Данная модель {0} не является наследником от '
                    'django.db.models.Model и m3.db.BaseEnumerate. '
                    'Задайте верный справочник'.format(reference_proxy.model)
                )

            self.values.update({key: {'model': '', 'title': '', 'kind': '', 'self_reference_field': '', 'fields': []}})
            if issubclass(reference_proxy, ReferenceProxy):
                self._initial_model_data(key, reference_proxy)
            elif issubclass(reference_proxy, ReferenceVirtualModelProxy):
                self._initial_virtual_model_data(key, reference_proxy)

    def _initial_virtual_model_data(self, key, reference_proxy):
        """
        Описываем справочник созданный на базе виртуальной модели
        :param key: Ключ справочника
        :type key: string
        :param reference_proxy: Прокси класс для работы с моделью
        :return: Заполненный данными словарик модели
        """
        self.values[key]['model'] = reference_proxy.model
        self.values[key]['title'] = reference_proxy.verbose_name

        # "kind": "P" модель плоская(не иерархичная) / "H" иерархичная
        self.values[key]['kind'] = ONE_LEVEL_MODEL
        self.values[key]['fields'] = self._get_fields_virtual_model(reference_proxy.required_fields)

    def _initial_model_data(self, key, reference_proxy):
        """
        Описываем справочник созданный на базе модели
        :param key: Ключ справочника
        :type key: string
        :param reference_proxy: Прокси класс для работы с моделью
        :return:  Заполненный данными словарик модели
        """
        self.values[key]['model'] = reference_proxy.model
        self.values[key]['title'] = reference_proxy.model._meta.verbose_name

        # "kind": "P" модель плоская(не иерархичная) / "H" иерархичная
        self.values[key]['kind'] = ONE_LEVEL_MODEL

        self_reference = self._model_hierarchic(reference_proxy.model)

        if self_reference:
            self.values[key]['self_reference_field'] = self_reference.field.name
            self.values[key]['kind'] = TREE_MODEL

        self.values[key]['fields'] = self._get_fields_model(reference_proxy.model, reference_proxy.required_fields)

    def _get_fields_virtual_model(self, required_fields):
        """
        Метод позволяет получить описание полей выбраной модели для запроса
        :param required_fields: Обязательные поля
        :type required_fields: list
        :return: Массив полей
        :rtype: list
        """
        result = list()
        for required_field in required_fields:
            field_description = {
                'name': required_field,
                'title': required_field,
                'type': self.type_fields[fields.CharField],
                'attrRefName': '',
                'allowFiltering': True,
            }

            result.append(field_description)
        return result

    def _get_fields_model(self, model, required_fields):
        """
        Метод позволяет получить описание полей выбраной модели для запроса
        :param model: Модель справочника
        :type model: django.db.models.Model
        :param required_fields: Обязательные поля
        :type required_fields: list
        :return: Массив полей
        :rtype: list
        """
        result = list()
        for required_field in required_fields:
            if required_field in [x.name for x in model._meta.get_fields()]:
                field = ModelOptions(model).get_field(required_field)
                try:
                    type_field = self.type_fields[field.__class__]
                except KeyError:
                    raise EdureceptionTypeError(
                        'Необходимо внести в словарь RefsListEnum.type_fields класс {0}'.format(field.__class__)
                    )

                field_description = {
                    'name': required_field,
                    'title': field.verbose_name,
                    'type': type_field,
                    'attrRefName': '',
                    'allowFiltering': True,
                }

                result.append(field_description)
        return result

    @staticmethod
    def _model_hierarchic(model):
        """
        Метод позволяет выяснить является модель иерархичной или нет
        :param model: Модель справочника
        :return: Если в модели есть связь саму на себя то она иерархичная
        :rtype: models.fields
        """
        result = None

        for rel in model._meta.fields:
            if hasattr(rel, 'field') and rel.field.model == model:
                result = rel
                break
        return result


def convert_reception_to_timeslot(reception):
    """
    Конвертирует инстанцию производную от AbstractReception в entities.SlotData
    :param reception: Назначеный прием
    :return: Запись о приеме в терминах Spyne
    """
    area_id = reception.timetablerecord.timetablecrontab.area_id
    slot = entities.SlotData(
        slotId='{0}'.format(reception.timetablerecord.id),
        areaId='{0}'.format(area_id),
        visitTime=reception.timetablerecord.begin,
        duration='{0}'.format(reception.timetablerecord.timetablecrontab.duration),
    )
    return slot


def find_free_slot_or_fail(slot_id):
    """
    Ищет свободный слот записи на прием. Если слод занят то кидает
    исключение. И сервис возвращает ответ с ошибкой.
    :param slot_id: id слота записи на прием
    :return: Слот записи оп приеме
    """

    try:
        time_table_record = TimeTableRecord.objects.get(id=slot_id)
    except (TimeTableRecord.DoesNotExist, ValueError):
        raise EdureceptionServiceError('Слота {0} не существует'.format(slot_id))
    booked_receptions = ApplicantReception.objects.filter(
        timetablerecord__id=time_table_record.id, status=ApplicantReception.STATUS_APPLIED
    )
    if booked_receptions.exists():
        raise EdureceptionServiceError('Слот уже занят')
    return time_table_record


def reserve_reception(book_id, applicant, time_table_record):
    """
    Резервирует слот расписания за заявителем.
    :param book_id: идентификатор запроса на бронирование
    :param applicant: заявитель
    :param time_table_record: слот записи о приеме
    :return: Заись о приеме
    """

    reception = ApplicantReception.objects.create(
        applicant=applicant,
        timetablerecord=time_table_record,
        status=ApplicantReception.STATUS_APPLIED,
        book_id=book_id,
    )

    return reception


def find_reception_or_fail(book_id, esia_id=None):
    """
    Ищем инстанцию записи о приеме. Кидаем исключение, если запись не нашли
    :param book_id: Идентификатор запроса на бронирование
    :param esia_id: ID Заявителя
    :return: ApplicantReception()
    :raises: EdureceptionServiceError
    """
    query_params = {'book_id': book_id}

    if esia_id:
        query_params['applicant_id'] = esia_id

    try:
        reception = ApplicantReception.objects.get(**query_params)
    except ApplicantReception.DoesNotExist:
        raise EdureceptionServiceError('Заявка о приеме {0} для заявителя {1} не найдена.'.format(book_id, esia_id))

    return reception
