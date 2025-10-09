# coding: utf-8
from __future__ import absolute_import, unicode_literals

import calendar
import datetime
import pickle
from collections import defaultdict

from dateutil import relativedelta
from django.conf import settings
from django.db import models, transaction
from django.db.models.base import ModelBase
from django.db.models.fields import FieldDoesNotExist
from django.utils.functional import cached_property
from educommon import ioc
from educommon.utils.date import WEEKDAYS
from future import standard_library
from future.builtins import object, range, str, zip
from future.utils import iteritems, with_metaclass
from m3 import RelatedError
from m3_django_compatibility import ModelOptions
from objectpack.models import VirtualModel

from .validators import BaseTimeTableValidator

standard_library.install_aliases()


class BaseWeekDaysVirtModel(VirtualModel):
    """
    Модель имитирует записи дней по неделям.

    (1-й понедельник, .., 5-й понедельник)
    """

    @staticmethod
    def postfix(day_idx):
        """
        Окончания для склонения номера недели по имени дня.
        :rtype: unicode
        """
        if day_idx == 6:
            # Воскресенье
            postfix = 'e'
        elif day_idx in [2, 4, 5]:
            # Среда, Пятница, Суббота
            postfix = 'я'
        else:
            postfix = 'й'
        return postfix

    @classmethod
    def _get_ids(cls, day_idx):
        """
        Генератор дней (1-й понедельник, .., 5-й понедельник).

        :params int day_idx: номер дня недели
        """
        from .base import AbstractCrontab

        # имя дня недели по номеру дня недели
        day_name = dict(AbstractCrontab.WEEKDAYS)[day_idx].lower()
        return (
            (i, '%s-%s %s' % (i, cls.postfix(day_idx), day_name))
            for i in range(1, AbstractCrontab.DEFAULT_WEEKS_COUNT + 1)
        )

    def __init__(self, param):
        (_id, name) = param
        self.id = _id
        self.name = name

    class _meta(object):
        verbose_name = 'Дни по номерам недель'
        verbose_name_plural = 'Дни по номерам недель'


class RequiredFieldsValidatorError(Exception):
    pass


class RequiredFieldsValidator(ModelBase):
    """
    Метакласс проверет все и поля моделей заданы в классах-наследниках.
    """

    def __new__(cls, name, bases, attrs):
        """
        В моделях которые не абстрактные пробегаем все классы
        иерархии и проверяем словари-аттрибуты `required_fields` на то все ли
        поля заданы в модели и корректного ли они типа.
        """
        model = super(RequiredFieldsValidator, cls).__new__(cls, name, bases, attrs)
        required_fields = {}
        if not model._meta.abstract:
            for checked_model in bases + (model,):
                fields = getattr(checked_model, 'required_fields', {})
                required_fields.update(fields)

        opts = ModelOptions(model)
        for field_name, field_type in iteritems(required_fields):
            try:
                field = opts.get_field_by_name(field_name)[0]
            except FieldDoesNotExist:
                msg = 'У модели {0} отсутствует поле {1}'.format(name, field_name)
                raise RequiredFieldsValidatorError(msg)

            if not isinstance(field, field_type):
                msg = 'Поле {0} модели {1} должно быть типа {2}'.format(field_name, name, field_type.__name__)
                raise RequiredFieldsValidatorError(msg)

        return model


class AbstractCrontab(with_metaclass(RequiredFieldsValidator, models.Model)):
    """Абстрактная модель сетки расписания приёма."""

    required_fields = {'specialist': models.ForeignKey, 'office': models.ForeignKey}

    validator_cls = None
    """
    Класс валидатора сохранения - наследник BaseTimeTableValidator
    """

    # выбор типа периодичности
    PERIOD_MONTH = 1
    PERIOD_WEEK = 2
    PERIOD_TYPES = [(PERIOD_MONTH, 'Ежемесячно'), (PERIOD_WEEK, 'Еженедельно')]

    # макс.значения продолжительности периода
    MAX_PERIOD_LENGTH = {PERIOD_MONTH: 12, PERIOD_WEEK: 60}

    # варианты продолжительности приема в минутах
    # значение в строках - для комбобокса
    DURATION_TYPES = [(1, '10'), (2, '20'), (3, '30'), (4, '40'), (5, '50'), (6, '60'), (7, '70'), (8, '80'), (9, '90')]
    # недель в месяце (и будет пять Понедельников, например)
    DEFAULT_WEEKS_COUNT = 5

    TIME_FORMAT = '%H:%M'

    # кортежи дней недели
    WEEKDAYS = WEEKDAYS

    # дата, с которой будет сформировано расписание приема
    date_begin = models.DateField('Дата начала')
    period_type = models.PositiveSmallIntegerField(
        verbose_name='Периодичность',
        choices=PERIOD_TYPES,
        default=PERIOD_MONTH,
    )
    # количество недель/месяцев
    period_length = models.PositiveSmallIntegerField(
        verbose_name='Продолжительность периода',
    )
    duration = models.PositiveSmallIntegerField(verbose_name='Продолжительность (мин.)', choices=DURATION_TYPES)

    """
    Хранит дамп настройки для формирования расписания в виде словаря
        {
            DAY_IDX: {'days': [2, 4, 5], 'begin': '17.45', 'end': '18.05'},
        }

    DAY_IDX - int, день из web_edu.core.fgos.schedule_template.models.WEEKDAYS
        например, Понедельник
    'days' - list, список int - номеров дней для периодичности PERIOD_MONTH
        например, [2, 4, 5] - 2-й, 4-й и 5-й Понедельник месяца
    'begin' - str, время начала
        например, 17:05
    'end' - str, время окончания
        например, 17:50

    Значение по ключу DAY_IDX может отсутствовать, это значит, что данный день
    не используется

    Поле - приватное, т.к. это дамп словаря, работать с ним нужно через
    свойство config
    """
    _config = models.TextField(verbose_name='Настройка расписания', default='')

    @property
    def config(self):
        # сPickle - чтобы не думать о типе данных
        return pickle.loads(str(self._config))

    @config.setter
    def config(self, config):
        self._config = pickle.dumps(config)

    @cached_property
    def _days_and_weeks(self):
        """
        Получение конфигурации месяца в виде словара.

        (зависимость номеров дней недели и номеров недель)
        :rtype: dict
        """
        # выбранные номера недель и дни недели в виде словаря
        days_and_weeks = defaultdict(list)
        week_range = list(range(1, self.DEFAULT_WEEKS_COUNT + 1))

        for day_idx, data in iteritems(self.config):
            if not data:
                continue

            _range = None
            if self.period_type == self.PERIOD_WEEK:
                _range = week_range
            else:
                if data['days']:
                    # дни были выбраны
                    _range = data['days']
            if _range:
                days_and_weeks[day_idx] = _range

        return days_and_weeks

    @cached_property
    def days_and_time(self):
        """
        Дни недели и датавремя (в формате datetime.datetime).

        :rtype: dict
        """

        def time(t):
            return datetime.datetime.strptime(t, self.TIME_FORMAT)

        return dict(
            (day_idx, (time(data['begin']), time(data['end']))) for day_idx, data in iteritems(self.config) if data
        )

    def __init__(self, *args, **kwargs):
        assert issubclass(self.validator_cls, BaseTimeTableValidator), (
            'Ожидается класс валидатора - наследник BaseTimeTableValidator'
        )
        super(AbstractCrontab, self).__init__(*args, **kwargs)

    def iterdates(self):
        """
        Генератор дат по настройкам self.config.

        :warn: Даты отдаются в неотсортированном виде: сначала все ПН месяца,
        потом все ВТ месяца, ..., далее - след. месяц
        :rtype: datetime.date
        """

        # обход по периодичностям
        cc = calendar.Calendar(calendar.MONDAY)
        # шаг итерации по календарю
        delta = relativedelta.relativedelta(months=1)
        date = self.date_begin

        # дата последнего дня для формирования исходя из дня начала и
        # длины периода
        key = 'weeks' if self.period_type == self.PERIOD_WEEK else 'months'
        last_date = self.date_begin + relativedelta.relativedelta(**{key: self.period_length})

        # цикл по месяцам
        while date <= last_date:
            year, month = date.year, date.month
            month_start_date = datetime.date(year, month, 1)

            # цикл по календарю месяца (по столбцам)
            for day_idx, dates in enumerate(zip(*cc.monthdatescalendar(year, month))):
                week_dates = [
                    w_date
                    for w_date in dates
                    if (
                        # только текущего месяца
                        w_date >= month_start_date
                        and
                        # позже даты старта
                        w_date >= self.date_begin
                        and
                        # и не позже даты окончания
                        w_date < last_date
                    )
                ]
                for week_idx in self._days_and_weeks[day_idx]:
                    try:
                        yield week_dates[week_idx - 1]
                    except IndexError:
                        pass
            date += delta

    def get_timedelta_duration(self):
        """
        Получение продолжительности в виде datetime.timedelta.

        :rtype: datetime.timedelta
        """
        return datetime.timedelta(seconds=int(dict(self.DURATION_TYPES)[self.duration]) * 60)

    def applicant_reception_msg(self):
        """
        Проверка на наличие назначенных приемов Посетителей.

        у специалиста из timetablecrontab
        :returns: сообщение о наличии либо пустую строку
        :rtype: unicode
        """
        message = ''

        all_slots = self.timetablerecord_set.all().values_list('id', flat=True)
        records = (
            ioc.get('edureception__ApplicantReception')
            .objects.filter(timetablerecord__in=all_slots)
            .values_list('timetablerecord_id', flat=True)
        )

        with_receptions = self.timetablerecord_set.filter(id__in=records)

        if with_receptions.exists():
            times = [
                begin.strftime('{0} {1}'.format(settings.DATE_FORMAT, self.TIME_FORMAT))
                for begin in with_receptions.values_list('begin', flat=True)
            ]

            fullname = self.specialist.fullname() if callable(self.specialist.fullname) else self.specialist.fullname

            message = 'У сотрудника {0} назначены приемы: {1}'.format(fullname, ', '.join(times))
        return message

    def clean(self):
        self.validator_cls(timetable=self)()

    def safe_delete(self):
        # нельзя удалять, раз посетителям назначены приемы
        has_child_msg = self.applicant_reception_msg()
        if has_child_msg:
            raise RelatedError(has_child_msg)
        else:
            self.delete_in_transaction()
        return True

    @transaction.atomic
    def delete_in_transaction(self):
        """
        Удаляем в транзакции связанные записи далее саму запись
        """
        self.timetablerecord_set.all().delete()
        super(AbstractCrontab, self).delete()

    @property
    def area_id(self):
        raise NotImplementedError

    class Meta(object):
        verbose_name = 'Расписание специалиста'
        abstract = True


class AbstractRecord(with_metaclass(RequiredFieldsValidator, models.Model)):
    """Абстрактная модель 'Прием' (запись сетки расписания)."""

    required_fields = {'timetablecrontab': models.ForeignKey}

    # текст в ячейке, когда на прием не назначены посетители
    NO_RECEPTION = 'Нет приема'

    begin = models.DateTimeField(verbose_name='С')
    end = models.DateTimeField(verbose_name='По')

    class Meta(object):
        abstract = True
        verbose_name = 'Приём специалиста'
        verbose_name_plural = 'Приёмы специалиста'


class AbstractReception(with_metaclass(RequiredFieldsValidator, models.Model)):
    """
    Абстрактная модель 'Назначенный приём'.

    (связка посетителя с приёмом в сетке расписания).
    """

    STATUS_APPLIED = 201
    STATUS_CANCELED = 301
    status_choices = (
        (STATUS_APPLIED, 'Исполнено'),
        (STATUS_CANCELED, 'Отменено'),
    )

    book_id = models.CharField(
        max_length=100,
        verbose_name='Идентификатор запроса на бронирование',
        unique=True,
        null=True,
        blank=True,
    )
    status = models.IntegerField(verbose_name='Статус приема', choices=status_choices, default=STATUS_APPLIED)

    reason_name = models.CharField(
        max_length=250,
        verbose_name='Причина записи на прием',
        null=True,
        blank=True,
    )

    reason = models.ForeignKey('edureception.Reason', related_name='reason_set', null=True, on_delete=models.SET_NULL)

    required_fields = {'applicant': models.ForeignKey, 'timetablerecord': models.ForeignKey}

    class Meta(object):
        abstract = True
        verbose_name = 'Назначенный приём'
        verbose_name_plural = 'Назначенные приёмы'
        unique_together = ('applicant', 'timetablerecord')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if update_fields is not None:
            update_fields = set(update_fields)

        self.reason_name = self.reason.name if self.reason else ''
        if update_fields is not None:
            update_fields.add('reason_name')

        kwargs = {
            'force_insert': force_insert,
            'force_update': force_update,
            'using': using,
            'update_fields': list(update_fields) if update_fields is not None else None,
        }

        super(AbstractReception, self).save(**kwargs)


class Proxy(object):
    """
    Proxy класс, который оборачивает модель в целевом проекте и добавлет
    необходимые интерфейсы, которые должны быть реализованы в произвоных
    моделях

    Например: Класс ApplicantProxy оборачивает модель `Заявитель` в
    целевом проекте (GTN, EDUSCHL). В производном классе от ApplicantProxy
    такжe должен быть реализован метод поиска и создания заявителя.
    """

    model = None


class ApplicantProxy(Proxy):
    def get_or_create(self, last_name=None, first_name=None, middle_name=None, document=None):
        """
        Ищет заявителя по заданым параетрам. Создает нового заявителя если
        модель не найдена.

        :param last_name: Фамилия
        :param first_name: Имя
        :param middle_name: Отчество
        :param document: Документ Заявителя
        :return: Инстанция модели заявителя
        :rtype: ApplicantProxy.model
        """
        raise NotImplementedError


class ReferenceProxy(Proxy):
    """
    Класс для передачи данных справочников.
    Модель должна быть наследником от django.db.models.Model.
    Используется в объявлении справочников: Reason, Organizations,
    IdentityDocumentsTypes
    """

    """
    Передаем список полей которые будут передоваться через сервисы
    Например в модели Reason
    [
        "name",
        "id"
    ]
    """
    required_fields = []

    def get_data(self, ordering):
        """
        Получение данных
        :param ordering: назначенная сортировка по полям
        :return: список данных
        :rtype: django.db.models.query.QuerySet
        """
        items = self.model.objects.all()
        if ordering:
            items = items.order_by(*ordering)
        return items

    def get_attribute_data(self, obj, attribute):
        """
        Получение данных поля
        :param obj: объект модели
        :type obj: object(models.Model)
        :param attribute: атрибут по которому необходимо получить значение
        :type attribute: string
        :return: данные поля
        :rtype: в зависимости от типа данных в модели
        """
        try:
            data = getattr(obj, attribute)
        except AttributeError:
            raise AttributeError('Данного атрибута {0} у модели {1} не существует'.format(attribute, self.model))
        return data


class ReferenceVirtualModelProxy(Proxy):
    """
    Класс для передачи данных справочников представленных в види виртуальной
    модели. Исспользуется в IdentityDocumentsTypes
    Модель должна быть наследником от m3.db.BaseEnumerate.
    """

    """
    Передаем список полей которые будут передаваться через сервисы
    Например в модели IdentityDocumentsTypes
    [
        "value",
        "id"
    ]
    """
    required_fields = []
    # Название справочника
    verbose_name = ''

    def get_data(self, ordering=''):
        """
        Получение данных
        :param ordering: назначенная сортировка по полям
        :return: список данных
        :rtype: list
        """
        # TODO: ordering нужно использовать при получении данных. Но так как
        # неизвестно какие будут сортировки остался этот параметр без внимания.
        # Если сортировок не будет то убрать за ненадобностью
        return self.model.get_choices()

    def get_attribute_data(self, obj, attribute):
        """
        Получение данных поля с эмуляцией id
        :param obj: Вектор данных
        :type obj: tuple(int, namedtuple('Value', ['value', 'uftt_code']))
        :param attribute: атрибут по которому необходимо получить значение
        :type attribute: string
        :return: данные поля
        :rtype: string
        """
        pk, row = obj
        if attribute == 'id':
            data = pk
        else:
            try:
                data = getattr(row, attribute)
            except AttributeError:
                raise AttributeError(
                    'Данного атрибута {0} у справочника {1} не существует'.format(attribute, self.model)
                )
        return data
