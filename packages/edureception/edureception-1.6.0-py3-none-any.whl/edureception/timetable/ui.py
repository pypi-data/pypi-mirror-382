# coding: utf-8
from __future__ import unicode_literals

from django.utils.dateformat import format
from educommon.objectpack.ui import BaseGridWindow, GridPanel
from educommon.utils.date import WEEKDAYS_DICT
from educommon.utils.ui import formed
from m3.actions.urls import get_pack_instance
from m3_ext.ui import all_components as ext
from objectpack.ui import BaseEditWindow, BaseSelectWindow


class ReceptionCellEditWin(BaseEditWindow):

    """Окно редактирования ячейки в расписании приема специалиста"""

    def __init__(self):
        super(ReceptionCellEditWin, self).__init__()
        self.template_globals = 'ui-js/reception-cell-edit-window.js'

    def set_params(self, params):
        self.title = 'Добавление записи на прием'
        self.width = 600
        self.height = 300

        record = params['record']

        self.field_specialist.set_value_from_model(
            record.timetablecrontab.specialist
        )

        self.field_reception_date.value = '{0}'.format(
            format(record.begin, 'd.m.Y')
        )

        self.field_reception_time.value = '{0} - {1}'.format(
            format(record.begin, 'H:i'),
            format(record.end, 'H:i'),
        )

        self.field_reception_office.value = '{0}'.format(
            record.timetablecrontab.office
        )

        self.field_reception_weekday.value = '{0}'.format(
            WEEKDAYS_DICT[record.begin.weekday()]
        )

    def _init_components(self):
        super(ReceptionCellEditWin, self)._init_components()

        self.field_specialist = ext.ExtDictSelectField(
            label='Специалист',
            read_only=True,
            name='specialist_id',
            display_field='fullname',
            pack='SpecialistSelectPack',
        )

        self.field_reception_date = ext.ExtStringField(
            label='Дата приема',
            name='reception_date',
            read_only=True,
        )

        self.field_reception_time = ext.ExtStringField(
            label='Время приема',
            name='reception_time',
            read_only=True,
        )

        self.field_reception_weekday = ext.ExtStringField(
            label='День недели',
            name='reception_weekday',
            read_only=True,
        )

        self.field_reception_office = ext.ExtStringField(
            label='Офис',
            name='reception_office',
            read_only=True,
        )

        self.field_reason = ext.ExtDictSelectField(
            label='Причина записи',
            name='reason_id',
            value_field='id',
            display_field='name',
            allow_blank=False,
            hide_trigger=False,
            hide_edit_trigger=True,
            pack='GTNReasonActionPack',
        )

        self.grid_applicant = ext.ExtObjectGrid(
            name='grid_applicant',
        )

        applicant_pack = get_pack_instance('ApplicantPack')
        applicant_pack.configure_grid(self.grid_applicant)
        self.grid_applicant.url_data = (
            applicant_pack.assigned_rows_action.get_absolute_url()
        )
        self.grid_applicant.top_bar.search_field.hidden = True
        self.grid_applicant.top_bar.button_refresh.hidden = True

        self.grid_applicant.action_new = applicant_pack.select_window_action
        self.grid_applicant.action_edit = applicant_pack.select_window_action
        self.grid_applicant.url_delete = 'fake'

        self.grid_applicant.local_edit = True
        self.grid_applicant.allow_paging = False
        self.grid_applicant.height = 110
        for col in self.grid_applicant.columns:
            col.sortable = False

        self.field_applicant_id = ext.ExtHiddenField(
            name='applicant_id',
        )

    def _do_layout(self):
        super(ReceptionCellEditWin, self)._do_layout()

        table = ext.ExtContainerTable(columns=5, rows=4)
        table.set_rows_height(25)
        self.form.items.append(table)

        table.set_item(0, 0, self.field_specialist, 5)
        table.set_item(1, 0, self.field_reception_date, 2)
        table.set_item(1, 2, self.field_reception_weekday, 3)
        table.set_item(2, 0, self.field_reception_time, 2)
        table.set_item(2, 2, self.field_reason, 3)
        table.set_item(3, 0, self.field_reception_office, 2)

        self.form.items.append(self.grid_applicant)

        self.form.items.append(self.field_applicant_id)


class TimeTableGridPanel(GridPanel):

    """Панель с гридом."""

    @classmethod
    def configure_grid(cls, grid, params):
        grid = super(TimeTableGridPanel, cls).configure_grid(grid, params)
        grid.force_fit = True
        grid.template_globals = 'ui-js/specialist-reception-grid.js'

        read_only = params.get('read_only')

        if not read_only:
            grid.url_new = grid.url_edit = params['add_url']
            grid.url_delete = params['delete_url']

        return grid


class TimeTableWindow(BaseGridWindow):

    """Окно 'Расписания приема'."""

    grid_panel_cls = TimeTableGridPanel

    def _init_components(self):
        super(TimeTableWindow, self)._init_components()
        self.date_fld = ext.ExtDateField(
            name='date', label='Дата', allow_blank=False
        )
        self.date_fld._listeners['specialkey'] = 'dateSpecialKeyChange'
        self.specialist_fld = ext.ExtDictSelectField(
            name='specialist_id',
            label='Специалист',
            display_field='fullname',
            hide_clear_trigger=False,
        )

        self.close_btn = self.btn_close = ext.ExtButton(
            name='close_btn',
            text='Закрыть',
            handler='function(){Ext.getCmp("%s").close();}' % self.client_id
        )
        self.print_btn = ext.ExtButton(
            text='Печать', icon_cls='print-icon',
            handler='function(){printSchedule();}'
        )

        # исключения для make_read_only
        self._mro_exclude_list.extend([
            self.close_btn, self.print_btn
        ])

    def _do_layout(self):
        # добавление фильтрующих полей в фильтрующую панель
        self.filter_cnt.filters.extend([
            self.date_fld, self.specialist_fld,
        ])
        super(TimeTableWindow, self)._do_layout()
        self.buttons.extend([self.print_btn, self.btn_close])

        self.filter_cnt.items.extend([
            formed(self.date_fld, width=150, label_width=35),
            ext.ExtContainer(layout='fit', style={'padding': '5px'}),
            formed(self.specialist_fld, width=300, label_width=70),
        ])
        self.items.extend([self.filter_cnt, self.grid_panel])

    def set_params(self, params):
        super(TimeTableWindow, self).set_params(params)
        self.template_globals = 'ui-js/specialist-reception-timetable-win.js'
        self.date_fld.value = params['date']
        self.specialist_fld.pack = params['specialist_pack']
        self.print_url = params['print_url']

        if params.get('default_specialist'):
            self.specialist_fld.set_value_from_model(
                params.get('default_specialist'))


class BaseReceptionSelectWindow(BaseSelectWindow):
    """Класс позволяет исключить кнопку обновить из top bar"""

    def _do_layout(self):
        super(BaseReceptionSelectWindow, self)._do_layout()
        self.grid.top_bar.items.remove(
            self.grid.top_bar.button_refresh
        )


class SpecialistSelectWindow(BaseReceptionSelectWindow):
    """Окно выбора специалиста без кнопки обновить"""
    pass


class ApplicantSelectWindow(BaseReceptionSelectWindow):
    """Окно выбора заявителя на прием"""

    def set_params(self, params):
        super(ApplicantSelectWindow, self).set_params(params)
        self.template_globals = 'ui-js/applicant-select-win.js'
        if params.get("record_id", None):
            self._set_config_value("record_id", params["record_id"])
            self.grid.store.base_params.update(
                {"record_id": params["record_id"]}
            )
        if params.get("is_editing", None):
            self._set_config_value("is_editing", params["is_editing"])
            self.grid.store.base_params.update(
                {"is_editing": params["is_editing"]}
            )
