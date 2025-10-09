# coding: utf-8
from __future__ import (
    unicode_literals,
)

from django.utils.translation import (
    gettext as _,
)
from m3_ext.ui.containers import (
    ExtContainerTable,
)
from m3_ext.ui.fields.simple import (
    ExtStringField,
)

from objectpack.ui import (
    BaseEditWindow,
)


class ReasonEditWindow(BaseEditWindow):
    """окно редактирования записи"""

    def __init__(self):
        super(ReasonEditWindow, self).__init__()
        self.width, self.height = 500, 220
        self.min_width, self.min_height = self.width, self.height

    def _init_components(self):
        super(ReasonEditWindow, self)._init_components()
        self.field_code = ExtStringField(name='code', max_length=50, label=_('Код'))
        self.field_name = ExtStringField(
            name='name',
            max_length=250,
            allow_blank=False,
            label=_('Причина записи'),
        )

    def _do_layout(self):
        super(ReasonEditWindow, self)._do_layout()

        table = ExtContainerTable(rows=2, columns=1)
        self.form.items.append(table)

        table.set_item(0, 0, self.field_code)
        table.set_item(1, 0, self.field_name)

    def set_params(self, params):
        super(ReasonEditWindow, self).set_params(params)
