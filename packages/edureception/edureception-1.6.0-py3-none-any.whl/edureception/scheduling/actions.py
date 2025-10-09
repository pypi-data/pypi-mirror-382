# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import abc
import datetime
from functools import partial

from django.core.exceptions import ValidationError
from django.db.transaction import atomic
from django.utils.functional import cached_property
from m3.actions import ApplicationLogicException
from objectpack.actions import ObjectPack
from objectpack.filters import ColumnFilterEngine, FilterByField

from future.builtins import object
from future.utils import iteritems, itervalues

from ..base import AbstractCrontab, BaseWeekDaysVirtModel


class ColumnFabric(object):

    """Создание колонок пака."""

    filter_engine_clz = ColumnFilterEngine
    column_name_on_select = 'specialist.fullname'

    def __init__(self):
        self._ff = partial(FilterByField, self.model)
        super(ColumnFabric, self).__init__()

    def col_fullname(self):
        return dict(
            data_index='specialist.fullname',
            header='Ф.И.О. специалиста',
            filter=self._ff(
                'specialist.fullname', 'specialist.fullname__icontains'),
            width=5,
            sortable=True
        )

    def col_date_begin(self):
        return dict(
            data_index='date_begin',
            header='Дата начала',
            filter=self._ff('date_begin', 'date_begin'),
            width=3,
            sortable=True
        )

    def col_office(self):
        return dict(
            data_index='office',
            header='Кабинет',
            filter=self._ff('office__number', 'office__number'),
            width=2,
            sortable=True
        )

    def col_period_type(self):
        return dict(
            data_index='period_type',
            header='Периодичность',
            filter=self._ff('period_type', 'period_type'),
            width=3,
            sortable=True
        )

    def col_period_length(self):
        return dict(
            data_index='period_length',
            header='Продолжительность<br/>периода',
            width=3,
            sortable=True
        )

    def col_days_display(self):
        return dict(
            data_index='days_display',
            header='Дни приема',
            width=3,
        )

    def col_time_display(self):
        return dict(
            data_index='time_display',
            header='Время приема',
            width=2,
        )

    def col_duration(self):
        return dict(
            data_index='duration',
            header='Продолжительность<br/>приема (мин.)',
            width=3,
            sortable=True
        )

    @property
    def columns(self):
        return [getattr(self, col)() for col in [
            'col_fullname',
            'col_date_begin',
            'col_office',
            'col_period_type',
            'col_period_length',
            'col_days_display',
            'col_time_display',
            'col_duration'
        ]]


class BaseReceptionSchedulingPack(ColumnFabric, ObjectPack):

    """Создание сетки расписания приема специалистов."""

    title = 'Формирование сетки расписания приемов'

    model = None
    """
    Продуктовая модель сетки расписания - наследник ``AbstractCrontab``.
    """

    list_window = None
    """
    Окно реестра сеток расписания приема
    - наследник ``objectpack.ui.BaseListWindow``
    """

    add_window = edit_window = None
    """
    Окна для настройки и генерации расписания сетки приема
    - наследник ``ui.ReceptionSchedulingAddWin``
    """

    @cached_property
    def WEEKDAYS_DICT(cls):
        return dict(cls.model.WEEKDAYS)

    @abc.abstractproperty
    def weekdays_select_pack(self):
        """
        Пак выбора дней недели - наследник BaseWeekDaysSelectPack.

        .. code::

            ControllerCache.find_pack(WeekDaysSelectPack)
        """
        pass

    def __init__(self):
        assert issubclass(
            self.model, AbstractCrontab
        ), "Модель {} должна быть наследником класса {}".format(
            self.model.__name__, AbstractCrontab.__name__
        )
        super(BaseReceptionSchedulingPack, self).__init__()

    def declare_context(self, action):
        result = super(
            BaseReceptionSchedulingPack, self).declare_context(action)

        if action is self.save_action:
            result.update(
                specialist_id={'type': 'int'},
                office_id={'type': 'int'},
                date_begin={'type': 'date'},
                period_type={'type': 'int'},
                period_length={'type': 'int'},
                duration={'type': 'int'}
            )
            # декларирование параметров панели "время приема"
            # некоторые параметры необязательные, некоторые зависимые,
            # поэтому здесь задекларирован только тип параметров

            for day_idx, _ in self.model.WEEKDAYS:
                result[self.add_window.chbox_name(day_idx)] = {
                    'type': 'boolean', 'default': False}
                result[self.add_window.dayselect_name(day_idx)] = {
                    'type': 'json_or_empty_str', 'default': ''}
                result[self.add_window.begin_name(day_idx)] = {
                    'type': 'str', 'default': ''}
                result[self.add_window.end_name(day_idx)] = {
                    'type': 'str', 'default': ''}

        """
        Дополнительная декларация контекста.

        .. code::

            # декларация значения элемента фильтра по периоду
            if action is self.rows_action:
                result['period_id'] = {'type': 'int', 'default': 0}
        """

        return result

    def get_rows_query(self, request, context):
        query = super(BaseReceptionSchedulingPack, self).get_rows_query(
            request, context)

        """
        Пример фильтра записей.

        .. code::

            if context.period_id != 0:
                # фильтр записей по периоду
                period = Period.objects.get(id=context.period_id)
                b, e = period.date_begin, period.date_end
                query = query.filter(date_begin__gte=b, date_begin__lte=e)
        """

        return query

    def prepare_row(self, obj, request, context):
        """Заполнение столбцов дни приема и время приема в реестре."""
        obj = super(BaseReceptionSchedulingPack, self).prepare_row(
            obj, request, context)

        days, times = [], []

        for day_idx, day_conf in iteritems(obj.config):
            if day_conf:
                days.append(self.WEEKDAYS_DICT[int(day_idx)])
                times.append(
                    '{0} - {1}'.format(day_conf['begin'], day_conf['end'])
                )
        obj.days_display = '<br/>'.join(days)
        obj.time_display = '<br/>'.join(times)

        return obj

    def get_edit_window_params(self, params, request, context):
        """Установка параметров окна."""
        params = super(
            BaseReceptionSchedulingPack, self
        ).get_edit_window_params(
            params, request, context)

        obj = params['object']

        # нельзя редактировать, раз есть назначнные приемы
        applicant_reception_msg = obj.applicant_reception_msg()
        if applicant_reception_msg:
            raise ApplicationLogicException(
                'Внимание! Вы не можете изменить запись. {0}'.format(
                    applicant_reception_msg)
            )

        # id типа периодичности "Ежемесячно"
        params['period_month_id'] = self.model.PERIOD_MONTH
        # макс.значения продолжительности периода
        params['max_period_length'] = self.model.MAX_PERIOD_LENGTH
        params['weekdays_select_pack'] = self.weekdays_select_pack.__class__

        if not params['create_new']:
            # биндинг
            self._obj_to_schedulepanel(obj)

        return params

    def _obj_to_schedulepanel(self, obj):
        """
        Биндинг из объекта в интерфейс.

        Инициализация конфигурации панели 'Время приема'
        в соответствующие аттрибуты obj (по именам контролов панели)

        """
        win = self.add_window  # шорткат
        is_month = obj.period_type == self.model.PERIOD_MONTH

        _set = lambda attr, val: setattr(obj, attr, val)

        for day_idx, day_conf in iteritems(obj.config):
            if day_conf:
                # чекбокс
                _set(win.chbox_name(day_idx), True)
                _set(win.begin_name(day_idx), day_conf['begin'])
                _set(win.end_name(day_idx), day_conf['end'])
                if is_month:
                    # был выбран тип периодичности "Ежемесячно"
                    # значит должен был быть выбран хотя бы один день
                    # в строковом виде
                    _set(
                        win.dayselect_name(day_idx),
                        (day_idx, day_conf['days'])
                    )

    def _schedulepanel_to_obj(self, obj, create_new, context):
        """
        Биндинг из интерфейса в объект.

        Сбор конфигурации с панели 'Время приема'
        в поле конфигурации модели obj.config для последующего сохранения
        """
        win = self.add_window  # шорткат
        config = {} if create_new else obj.config
        is_month = context.period_type == self.model.PERIOD_MONTH

        _get = lambda attr: getattr(context, attr)
        for day_idx, _ in self.model.WEEKDAYS:
            # поставлен ли чекбокс
            if _get(win.chbox_name(day_idx)):
                config[day_idx] = {
                    'begin': _get(win.begin_name(day_idx)),
                    'end': _get(win.end_name(day_idx)),
                    'days': _get(
                        win.dayselect_name(day_idx)) if is_month else None
                }
            else:
                config[day_idx] = None

        obj.config = config

    def _check_before_save(self, obj, create_new, request, context):
        """Проверки на корректность сохраняемых данных."""
        try:
            obj.full_clean()
        except ValidationError as exc:
            flat_messages = [
                m for mess in itervalues(exc.message_dict) for m in mess
            ]
            raise ApplicationLogicException(
                'В процессе формирования сетки расписания обнаружены ошибки:'
                '<br/>- %s' % '<br/>- '.join(flat_messages)
            )

        # нельзя редактировать, раз посетителям назначены приемы
        applicant_reception_msg = obj.applicant_reception_msg()
        if applicant_reception_msg:
            raise ApplicationLogicException(applicant_reception_msg)

    def _delete_old_before_save(self, obj, create_new, request, context):
        """Удаление старых записей в сетке расписания."""
        obj.timetablerecord_set.all().delete()

    def _create_new_schedule(self, obj, request, context):
        # создание новой сетки
        combine = datetime.datetime.combine
        delta = obj.get_timedelta_duration()

        for date in obj.iterdates():

            begin, end = obj.days_and_time.get(date.weekday())
            time_begin = begin
            # записи по интервалам времени
            while time_begin < end:
                time_end = time_begin + delta

                self._create_timetable_record(
                    timetablecrontab=obj,
                    begin=combine(date, time_begin.time()),
                    end=combine(date, time_end.time())
                )

                time_begin += delta

    @abc.abstractmethod
    def _create_timetable_record(self, timetablecrontab, begin, end):
        """
        Создание приема в сетке расписания.

        .. code::

            models.TimeTableRecord.objects.create(
                timetablecrontab=timetablecrontab, begin=begin, end=end
            )
        """

    @atomic
    def save_row(self, obj, create_new, request, context):
        # Сбор конфигурации с панели 'Время приема'
        self._schedulepanel_to_obj(obj, create_new, context)
        # проверки на корректность сохраняемых данных
        self._check_before_save(obj, create_new, request, context)
        # удаление старых записей
        self._delete_old_before_save(obj, create_new, request, context)

        super(BaseReceptionSchedulingPack, self).save_row(
            obj, create_new, request, context)
        # создание приемой сетки расписания
        self._create_new_schedule(obj, request, context)

    def extend_menu(self, menu):
        """
        Добавление в меню "Пуск"

        .. code::

            return menu.SubMenu(
                'Зачисление', menu.Item(self.title, self.list_window_action))
        """


class BaseWeekDaysSelectPack(ObjectPack):
    """
    Пак множественного выбора дней.

    Возвращает перечень дней "1-й понедельник, ..., 5-й понедельник".
    """

    model = None
    """
    Имя продуктовой модели виртуальх дней недели.

    Наследник BaseWeekDaysVirtModel
    """

    columns = [{'data_index': 'name', 'header': 'Дни'}]
    column_on_select = 'name'

    def __init__(self):
        assert issubclass(
            self.model, BaseWeekDaysVirtModel
        ), "Модель {} должна быть наследником класса {}".format(
            self.model.__name__, BaseWeekDaysVirtModel.__name__
        )
        super(BaseWeekDaysSelectPack, self).__init__()

    def declare_context(self, action):
        result = super(BaseWeekDaysSelectPack, self).declare_context(action)
        if action is self.rows_action:
            result['day_idx'] = {'type': 'int'}
        return result

    def get_rows_query(self, request, context):
        return self.model.objects.configure(day_idx=context.day_idx)

    def get_display_dict(
        self, param, value_field='id', display_field='name'
    ):
        """Реализация интерфейса для биндинга мультиселектфилда."""
        (day_idx, selected) = param
        return [{
            value_field: day.id,
            display_field: day.name
        } for day in self.model.objects.configure(day_idx=day_idx).filter(
            id__in=selected
        )]
