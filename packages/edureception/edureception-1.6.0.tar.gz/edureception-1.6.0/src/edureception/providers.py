# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import abc
import datetime
from collections import defaultdict

from django.conf import settings
from django.db.models import Q
from django.utils.functional import cached_property
from educommon import ioc
from educommon.report import (AbstractDataProvider, BaseProviderAdapter,
                              DependentCompositeProvider)
from educommon.utils.date import get_weekdays_for_date

from future.builtins import object, zip
from future.utils import iterkeys, itervalues

from . import base


class AbstractModelView(AbstractDataProvider):

    """Представление данных Модели по списку имен ее полей."""

    data = None  # данные будут здесь

    model = None
    """
    Модель (источник данных)

    .. code::

        model = TimeTableCrontab
    """

    _values_params = None
    """
    Параметры выгрузки данных (будут дополнены ``id``)

    .. code::

        _values_params = [
            'specialist__info_date_begin',
            'specialist__info_date_end',
            'specialist__person__fullname',
        ]
    """

    def __init__(self):
        assert self.model, "Не определен источник данных (model)"
        assert self._values_params, (
            "В провайдере '{}' должны быть указаны"
            " параметры для выгрузки данных _values_params".format(
                self.__class__.__name__
            )
        )
        super(AbstractModelView, self).__init__()

    @property
    def q_filter(self):
        """
        Дополнительные условия фильтрации записей модели.
        :rtype: django.db.models.Q
        """
        return Q()

    def load_data(self):
        """Метод загрузки данных."""
        # загрузка данных вынесена в отдельный метод
        # т.к. к load_data обращается Общий провайдер сетки расписания
        self.data = self._get_data()

    def _get_data(self):
        """Формирование структуры данных."""
        values_params = ['id', ]
        values_params.extend(self._values_params)

        return dict((
            d['id'], d
        ) for d in self.model.objects.filter(
            self.q_filter
        ).values(*values_params))


class BaseSpecialistDataProvider(AbstractModelView):

    """Провайдер данных специалистов, задействованных в расписании приёмов."""

    data = None  # данные будут здесь

    model = None
    """
    Продуктовая модель (реализация) сетки расписания
    Т.к. интересуют только специалисты, имеющие назначенные приемы
    то продуктовая модель - модель расписания приема ``AbstractCrontab``

    .. code::

        model = TimeTableCrontab
    """

    _values_params = None
    """
    Параметры выгрузки данных (будут дополнены ``specialist_id``)

    .. code::

        _values_params = [
            'specialist__info_date_begin',
            'specialist__info_date_end',
            'specialist__person__fullname',
        ]
    """

    def __init__(self):
        assert issubclass(
            self.model, base.AbstractCrontab
        ), 'Ожидается модель - наследник AbstractCrontab'
        super(BaseSpecialistDataProvider, self).__init__()

    def init(self, date_from, date_to, specialist_id=None, **params):
        """
        Установка параметров значений из ui-компонент фильтров расписания.

        Может быть дополнено:

        .. code::

            # ограничение выборки специалистов по учреждению
            self._school_id = params['school_id']
        """
        # 'дата с' расписания приема специалистов
        self._date_from = date_from
        # 'дата по' расписания приема специалистов
        self._date_to = date_to
        # конкретный специалист (если выбран в качестве фильтра)
        self._specialist_id = specialist_id

    @property
    def q_filter(self):
        """
        Дополнительные условия фильтрации специалистов расписания приема.

        .. note::

            Т.к. интересуют только специалисты, имеющие назначенные приемы
            то исходая модель - модель расписания приема ``TimeTableCronTab``

        .. code::

            # пример доп фильтра для школ
            specialists_filter = Q(**{
                # фильтр по учреждению
                'specialist__school': self._school_id,
                # фильтр по интервалу работы сотрудника
                'specialist__info_date_begin__lte': self._date_to,
                'specialist__info_date_end__gte': self._date_from,
                'specialist__depersonalized': False
            })

        :rtype: django.db.models.Q
        """

        # если был указан ``self._specialist_id`` то записи фильтруются по нему
        return Q(
            specialist_id=self._specialist_id
        ) if self._specialist_id else Q()

    def _get_data(self):
        """
        Формирование структуры данных о сотрудниках, осуществляющих прием.

        .. code::

            # пример кода выгрузки 'вручную'
            data = dict((
                specialist_id,
                {
                    'begin': info_date_begin,
                    'end': info_date_end,
                    'fullname': fullname
                }
            ) for (
                specialist_id,
                info_date_begin,
                info_date_end,
                fullname
            ) in self.model.objects.filter(
                self.q_filter
            ).values_list(
                'specialist_id',
                'specialist__info_date_begin',
                'specialist__info_date_end',
                'specialist__person__fullname',
            ))
            return data

        """
        values_params = ['specialist_id']
        values_params.extend(self._values_params)

        return dict((
            d['specialist_id'], d
        ) for d in self.model.objects.filter(
            self.q_filter
        ).values(*values_params))


class BaseOfficeDataProvider(AbstractModelView):

    """Провайдер данных отображения кабинетов."""

    model = ioc.get('edureception__Office')
    _values_params = None
    """
    Параметры выгрузки данных будут дополнены ``id`` модели ``models.Office``

    .. code::

        _values_params = [
            'number',
            'location__name',
        ]
    """


class BaseApplicantDataProvider(AbstractModelView):

    """Провайдер данных отображения посетителей приёма."""

    data = None  # данные будут здесь
    model = ioc.get('edureception__Applicant').model

    _values_params = None
    """
    Параметры выгрузки данных дополняются ``id`` модели ``models.Applicant``

    .. code::

        _values_params = [
            'fullname',
        ]
    """


class BaseTimeTableRecordProvider(AbstractDataProvider):

    """Провайдер сетки расписания"""

    # порядок сортировки ячеек в столбце
    _cell_order_by = ('begin', )

    # будут инжектироваться в инстанс снаружи
    specialists = None
    offices = None
    applicants = None

    """
    Продуктовая модель - наследник ``AbstractRecord``

    .. code::

        model = TimeTableRecord
    """

    @abc.abstractproperty
    def _time_format(self):
        """
        Формат времени.

        .. code::

            # 'HH:MM'
            return TimeTableCrontab.TIME_FORMAT
        """

    @property
    def q_filter(self):
        """Ограничение записей по датам."""
        dt = datetime.datetime.combine(self.date_to, datetime.time(23, 59, 59))
        return Q(
            begin__lte=dt,
            end__gte=self.date_from,
            timetablecrontab__specialist__in=set(iterkeys(self.specialists))
        )

    def __init__(self):
        super(BaseTimeTableRecordProvider, self).__init__()
        assert issubclass(
            self.model, base.AbstractRecord
        ), 'Ожидается модель - наследник AbstractRecord'

    def init(self, date_from, date_to, **params):
        """
        Установка параметров значений из ui-компонент фильтров расписания.

        .. code::

            self._school_id = school_id
        """
        self.date_from = date_from
        self.date_to = date_to

        # заинженктиться снаружи
        self.specialists = None
        self.offices = None
        self.applicants = None

    def load_data(self):
        """Метод загрузки данных."""
        # загрузка данных вынесена в отдельный метод
        # т.к. к load_data обращается Общий провайдер сетки расписания
        self.data = self._get_data()

    def _get_data(self):
        """
        Данные расписанию в виде словаря по каждому специалисту.

        Внутри каждого - словарь по датам (по колонкам)
        Внутри даты - список строк по времени начала
        """

        data = defaultdict(lambda: defaultdict(list))

        for (
            _id,
            begin,
            end,
            office_id,
            specialist_id,
        ) in self.model.objects.filter(
            self.q_filter
        ).values_list(
            'id',
            'begin',
            'end',
            'timetablecrontab__office',
            'timetablecrontab__specialist',
        ).order_by(*self._cell_order_by):

            ApplicantReception = ioc.get('edureception__ApplicantReception')
            try:
                applicant_reception = ApplicantReception.objects.filter(
                    timetablerecord=_id
                )[0]
            except (IndexError, KeyError):
                applicant_id = None
                reason_name = None
            else:
                applicant_id = applicant_reception.applicant_id
                reason_name = applicant_reception.reason_name

            specialist_data = self.specialists.get(specialist_id)
            if not specialist_data:
                # уволен, например
                continue

            # ислючение записи по дополнительным условиям бизнес логики.
            if not self.additional_terms(
                specialist_data, begin, end, office_id, applicant_id
            ):
                continue

            day_idx = begin.weekday()
            data[specialist_id][begin.date()].append((
                day_idx,
                self._get_cell_data(
                    _id, begin, end, office_id, applicant_id, reason_name
                )
            ))
        return data

    def _get_cell_data(
            self, _id, begin, end, office_id, applicant_id, reason_name):
        """Структура ячейки."""
        applicant = self.applicants.get(applicant_id)

        return {
            'record_id': _id,
            'begin': begin.strftime(self._time_format),
            'end': end.strftime(self._time_format),
            'office': self.offices.get(office_id),
            # причина записи на прием
            'reason': reason_name if reason_name else '',
            # Ф.И.О. посетителя
            'fullname': applicant['fullname'] if applicant else ''
        }

    def additional_terms(
        self, specialist_data, begin, end, office_id, applicant_id
    ):
        """
        Проверка дополнительных условий бизнес логики фильтрации.

        Например, специалист может уже не работать на дату приема

        .. code::

            # если сотрудник уже не работает на дату приема
            if not specialist_data['begin'] <= end and (
                specialist_data['end'] >= begin
            ):
                return False
        """
        return True


class BaseTimeTableProvider(DependentCompositeProvider):

    """Общий Провайдер данных для сетки расписания."""

    providers_order = None
    """
    Подпровайдеры и порядок их загрузки.

    .. code::

        providers_order = (
            # провайдер специалистов
            ('_specialists_provider', SpecialistDataProvider),
            # провайдер кабинетов
            ('_offices_provider', OfficeDataProvider),
            # провайдер посетителей
            ('_applicants_provider', ApplicantsDataProvider),
            # провайдер записей сетки расписания
            ('_timetable_provider', TimeTableRecordProvider),
        )

    """

    _dependence_map = {
        '_timetable_provider': {
            'specialists': ('_specialists_provider', 'data'),
            'offices': ('_offices_provider', 'data'),
            'applicants': ('_applicants_provider', 'data'),
        }
    }

    def __init__(self):
        assert self.providers_order, "Не определены подпровайдеры"

        # проверка соответствия классов провайдеров, аттрибутов и их порядка
        for (provider_name, provider_class), (name, subclass) in zip(
            self.providers_order,
            (
                ('_specialists_provider', BaseSpecialistDataProvider),
                ('_offices_provider', BaseOfficeDataProvider),
                ('_applicants_provider', BaseApplicantDataProvider),
                ('_timetable_provider', BaseTimeTableRecordProvider),
            )
        ):
            if provider_name != name:
                raise AssertionError(
                    "Некорректно указан аттрибут '{}' провайдера '{}'. "
                    "Ожидался {}".format(
                        provider_name, provider_class.__name__, name)
                )
            if not issubclass(provider_class, subclass):
                raise AssertionError(
                    "Провайдер '{}'' должен быть наследником '{}'".format(
                        provider_class.__name__, subclass.__name__)
                )

        super(BaseTimeTableProvider, self).__init__()

    def init(self, **params):
        super(BaseTimeTableProvider, self).init(**params)
        self._specialist_id = params['specialist_id']

        """
        .. code::
            # пример дополнительного параметра фильтрации - учреждение
            self._school_id = params['school_id']
        """

    @property
    def timetable_data(self):
        return self._timetable_provider.data


class TimeTableGridAdapter(BaseProviderAdapter):

    """Адаптер данных для ui-грида сетки расписания."""

    @cached_property
    def _no_reception(self):
        """Сообщение в свободной от приёма ячейке."""
        return self.provider._timetable_provider.model.NO_RECEPTION

    def _transpose(self, data):
        """
        Транспонирование, данные будут по строкам.

        Из списка словарей делается один словарь - по строке
        :rtype: list
        """
        result = []

        for day_data in zip(*data):
            row_dict = {}
            for day_idx, cell in day_data:
                row_dict[self.get_data_index(day_idx)] = cell
            result.append(row_dict)
        return result

    def get_data_index(self, day_idx):
        """
        Формирование data-index колонки.

        Должно совпадать с формировние data-index в построителе колонок.
        """
        return ColumnConstructor.get_data_index(day_idx)

    def get_rows(self, specialist_id):
        """
        Преобразование данных и получение строк.

        Дополнение недостающих ячеек значением 'Нет приема' до макс.значения
        кол-ва приемов в день (за 7 дней, начиная с date_from),
        чтобы в каждом из столбцов была равное количество строк.

        :rtype: list
        """
        specialist_data = self.provider.timetable_data[specialist_id]
        if not specialist_data:
            return []

        week = enumerate(date for _, date in get_weekdays_for_date(
            self.provider._timetable_provider.date_from))

        max_day_len = max(len(v) for v in itervalues(specialist_data))
        data = []

        for idx, date in week:
            datedata = specialist_data.get(date, [])

            datedata.extend(
                [(idx, self._no_reception), ] * (max_day_len - len(datedata))
            )

            data.append(datedata)

        return self._transpose(data)


class ColumnConstructor(object):

    """Колонки грида расписания."""

    column_param_name = 'day_idx'

    def __init__(self, date):
        """
        Инициализация.

        :param datetime.date date: дата, отн-но которой будет получена неделя
        """
        self.date = date

    def create_columns(self):
        """Построение колонок."""

        columns = []
        for day_name, date in get_weekdays_for_date(self.date):
            columns.append({
                'data_index': self.get_data_index(date.weekday()),
                'header': '<b>%s</b><br/>%s' % (
                    day_name, date.strftime(settings.DATE_FORMAT)),
                'column_renderer': 'specalistScheduleColumnRenderer'
            })
        return columns

    @classmethod
    def get_data_index(cls, day_idx):
        """Ключ дата-индекс колонки."""
        return '%s_%i' % (cls.column_param_name, day_idx)
