# coding: utf-8
from __future__ import unicode_literals

from m3_ext.ui import all_components as ext
from objectpack.ui import BaseEditWindow


class ReportWindow(BaseEditWindow):

    """Окно параметров отчета."""

    def _init_components(self):
        super(ReportWindow, self)._init_components()
        self.date_begin_fld = ext.ExtDateField(
            label='Дата с', name='date_from', allow_blank=False, anchor='100%'
        )
        self.date_end_fld = ext.ExtDateField(
            label='Дата по', name='date_to', allow_blank=False, anchor='100%')
        self.specialist_fld = ext.ExtDictSelectField(
            name='specialist_id',
            display_field='fullname',
            hide_clear_trigger=False,
            hide_edit_trigger=True,
            allow_blank=False,
            anchor='100%'
        )

    def _do_layout(self):
        super(ReportWindow, self)._do_layout()
        self.form.items.extend([
            self.date_begin_fld, self.date_end_fld, self.specialist_fld
        ])

    def set_params(self, params):
        super(ReportWindow, self).set_params(params)
        self.template_globals = 'ui-js/specialist-reception-report-win.js'
        self.height = 160
        self.width = 300
        self.maximizable = self.resizable = False
        self.specialist_fld.pack = params['specialist_select_pack']
        self.specialist_fld.label = params.get(
            'specialist_field_label', "Специалист")

        date_from, date_to = params.get('date_from'), params.get('date_to')
        specialist = params.get('specialist')

        if specialist and date_from and date_to:
            self.specialist_fld.set_value_from_model(params['specialist'])
            self.date_begin_fld.value = date_from
            self.date_end_fld.value = date_to
        else:
            self.specialist_fld.make_read_only()
        self.cancel_btn.handler = (
            "function(){Ext.getCmp('%s').close(true)}" % self.client_id)
