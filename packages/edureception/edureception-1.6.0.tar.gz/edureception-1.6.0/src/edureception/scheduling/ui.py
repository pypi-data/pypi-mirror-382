# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import json

from educommon import ioc
from educommon.utils.ui import formed
from m3_ext.ui import all_components as ext
from objectpack.ui import BaseListWindow, ModelEditWindow

from ..base import AbstractCrontab

observer = ioc.get('observer')


class BaseReceptionSchedulingWin(BaseListWindow):

    """Окно для формирования сетки расписания приема специалистов."""

    def _init_components(self):
        super(BaseReceptionSchedulingWin, self)._init_components()

        """
        Дополнение интерфейсаокна списка для реализации доп. фильтрации.

        .. code::

            self.grid.top_bar.filter_fld = objectpack.ui.make_combo_box(
                name='period_id',
                label='Период',
                data=[(0, 'Не выбрано')],
                allow_blank=False
            )
            self._mro_exclude_list.append(self.grid.top_bar.filter_fld)
        """

    def _do_layout(self):
        super(BaseReceptionSchedulingWin, self)._do_layout()

        """

        .. code::

            self.grid.top_bar.items.extend([
                SimpleToolbarSeparator(),
                self.grid.top_bar.filter_fld
            ])
        """

    def set_params(self, params):
        super(BaseReceptionSchedulingWin, self).set_params(params)
        self.maximized = True
        self.grid.sm = ext.ExtGridCheckBoxSelModel()

        """
        .. code::

            self.template_globals = 'ui-js/reception-scheduling-list.js'
            self.grid.top_bar.filter_fld.data.extend(params['periods'])
            self.grid.top_bar.filter_fld.value = params['current_period']
        """


def make_time_fld(name, label):
    """Создание элемента управления времени."""
    return ext.ExtStringField(
        name=name,
        label=label,
        input_mask='##:##',
        empty_text='в фомате ЧЧ:ММ',
        regex=r'^(([01]\d)|(2[0123])):[012345]\d$',
        mask_re=r'[\d\:]',
        allow_blank=False
    )


class BaseReceptionSchedulingAddWin(ModelEditWindow):
    """Окно добавления сетки расписания приема специалиста."""

    model = None
    """
    Продуктовая модель расписания приема специалистов.

    Наследник ``AbstractCrontab``
    """

    field_fabric_params = {
        'model_register': observer,
        'field_list': [
            'specialist_id',
            'office_id',
            'date_begin',
            'period_type',
            'period_length',
            'duration',
        ]
    }

    # префиксы полей настройки расписания ('Время приема')
    _pref_chbox = 'chbox_'
    _pref_dayselect = 'dayselect_'
    _pref_begin = 'begin_'
    _pref_end = 'end_'

    @staticmethod
    def _week_pack():
        """
        Пак - источник данных для контрола выбора дней недели.

        TODO: передавать в параметрах
        """
        assert False, "Доделать!"

    @staticmethod
    def _format(prefix, idx):
        return '{0}{1}'.format(prefix, idx)

    @classmethod
    def chbox_name(cls, day_idx):
        """Имя контрола чекбокса."""
        return cls._format(cls._pref_chbox, day_idx)

    @classmethod
    def dayselect_name(cls, day_idx):
        """Имя контрола с выбором номеров дней недели."""
        return cls._format(cls._pref_dayselect, day_idx)

    @classmethod
    def begin_name(cls, day_idx):
        """Имя контрола времени начала."""
        return cls._format(cls._pref_begin, day_idx)

    @classmethod
    def end_name(cls, day_idx):
        """Имя контрола времени окончания."""
        return cls._format(cls._pref_end, day_idx)

    @classmethod
    def _make_daytime_cmp(cls, week_day_idx, week_day_name):
        """
        Возвращает контейнер с полями выбора дня (или нескольких дней), времени

        :param int week_day_idx: индекс дня недели
        :param unicode week_day_name: имя дня недели
        :rtype: ext.ExtContainer
        """
        container = ext.ExtContainer(
            flex=len(cls.model.WEEKDAYS), style={'padding': '5px'})
        # чекбокс дня недели
        container.chbox_fld = ext.ExtCheckBox(
            name=cls.chbox_name(week_day_idx), box_label=week_day_name)
        # выбор номера недели в случае "Ежемесячно"
        container.days_select_fld = ext.ExtMultiSelectField(
            hide_edit_trigger=True,
            hide_dict_select_trigger=True,
            hide_trigger=False,
            hide_clear_trigger=True,
            handler_beforerequest='daySelectFldBeforeSelect',
            allow_blank=False,
            label='Выбор дня: %s' % week_day_name.lower()
        )
        # нейм затирается где-то в инитах :(
        container.days_select_fld.name = cls.dayselect_name(week_day_idx)
        container.days_select_fld.store._listeners['beforeload'] = (
            'function(){ daySelectFldBeforeSelect(Ext.getCmp("%s"))}' % (
                container.days_select_fld.client_id)
        )
        # поля времени
        container.time_begin_fld = make_time_fld(
            label='С', name=cls.begin_name(week_day_idx))
        container.time_end_fld = make_time_fld(
            label='По', name=cls.end_name(week_day_idx))

        combo_cnt = ext.ExtContainer(
            style={'padding-bottom': '2px', 'padding-top': '2px'}, layout='fit'
        )
        combo_cnt.items.append(container.days_select_fld)

        # контейнер, который будет выключаться (и выключать свои элементы)
        # в зависимости от container.chbox_fld
        container.read_only_cnt = ext.ExtContainer(layout='form')
        container.read_only_cnt.items.extend([
            combo_cnt,
            formed(container.time_begin_fld, label_width=20),
            formed(container.time_end_fld, label_width=20),
        ])
        container.read_only_cnt.make_read_only()

        container.items.extend([container.chbox_fld, container.read_only_cnt])
        return container

    def __init__(self):

        assert issubclass(
            self.model, AbstractCrontab
        ), "Модель {} должна быть наследником {}".format(
            self.model.__name__, AbstractCrontab.__name__
        )
        super(BaseReceptionSchedulingAddWin, self).__init__()

    def _init_components(self):
        super(BaseReceptionSchedulingAddWin, self)._init_components()
        self.top_cnt = ext.ExtContainer(layout='form')
        self.top_conf_cnt = ext.ExtContainer(layout='hbox', height=80)
        self.top_left_conf_cnt = ext.ExtContainer(layout='form', flex=2)
        self.top_right_conf_cnt = ext.ExtContainer(
            layout='form', flex=2, label_width=175,
            style={'padding-left': '5px'}
        )

        self._init_schedule_panel()

    def _init_schedule_panel(self):
        """Создание панели "Время приема"."""

        self.schedule_panel = ext.ExtPanel(
            header=True,
            title='Время приема',
            layout='form',
            body_cls="x-window-mc"
        )
        self.schedule_cnt = ext.ExtContainer(layout='hbox', height=100)

        # элементы, зависящие от выбора типа периода "Ежемесячно"
        dependent_field_periodtype_items = {}
        # эелементы, зависящие от чекбоксов
        dependent_chbox_items = {}
        # список контейнеров по дням недели
        self.day_containers = []

        for week_day_idx, week_day_name in self.model.WEEKDAYS:
            day_container = self._make_daytime_cmp(week_day_idx, week_day_name)
            self.day_containers.append(day_container)
            setattr(self.form, 'cnt_%i', day_container)

            # зависимость чекбокса и контейнера с временем и номером недели
            dependent_chbox_items[day_container.chbox_fld.client_id] = (
                day_container.read_only_cnt.client_id)
            # зависимые поля от выбора типа периода "Ежемесячно"
            dependent_field_periodtype_items[
                day_container.chbox_fld.client_id
            ] = day_container.days_select_fld.client_id

        self.dependent_chbox_items = json.dumps(dependent_chbox_items)
        self.dependent_field_periodtype_items = json.dumps(
            dependent_field_periodtype_items)

    def _do_layout(self):
        super(BaseReceptionSchedulingAddWin, self)._do_layout()
        self.form.items[:] = [
            self.top_cnt,
            self.top_conf_cnt,
            self.schedule_panel
        ]

        self.top_conf_cnt.items.extend([
            self.top_left_conf_cnt, self.top_right_conf_cnt,
        ])
        self.top_cnt.items.append(self.field__specialist_id)
        self.top_left_conf_cnt.items.extend([
            self.field__date_begin,
            self.field__period_type,
            self.field__office_id,
        ])
        self.top_right_conf_cnt.items.extend([
            self.field__duration, self.field__period_length
        ])

        self.schedule_cnt.items.extend(self.day_containers)
        self.schedule_panel.items.append(self.schedule_cnt)

    def set_params(self, params):
        # обход полей множественного выбора дней недели
        # которым из параметров необходимо назначить пак выбора дней недели
        for day_container in self.day_containers:
            day_container.days_select_fld.pack = params['weekdays_select_pack']
        super(BaseReceptionSchedulingAddWin, self).set_params(params)
        self.template_globals = 'ui-js/reception-scheduling-edit.js'
        self.dayselect_prefix = self._pref_dayselect
        self.width = 800
        self.height = 310
        self.resizable = False

        # значение "Ежемесячно"
        self.field__period_type.period_month_id = params['period_month_id']
        obj = params['object']
        # допустимые макс.значения поля "Продолжительность периода"
        max_length = params['max_period_length']
        self.field__period_length.max_value = max_length[obj.period_type]
        # меньше чем один период - не имеет смысла
        self.field__period_length.min_value = 1
        # данные о макс значениях (для изменения)
        self.field__period_length.max_period_length = json.dumps(max_length)
