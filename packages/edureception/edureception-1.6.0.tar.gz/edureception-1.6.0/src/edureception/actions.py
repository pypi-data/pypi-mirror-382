# coding: utf-8
from __future__ import (
    unicode_literals,
)

from functools import (
    partial,
)

from django.utils.translation import (
    gettext as _,
)
from edureception.models import (
    Reason,
)
from edureception.ui import (
    ReasonEditWindow,
)

from educommon import (
    ioc,
)
from objectpack.actions import (
    ObjectDeleteAction,
    ObjectPack,
)
from objectpack.filters import (
    ColumnFilterEngine,
    FilterByField,
)


class ReasonActionPack(ObjectPack):
    """Экшн для работы с справочником причин записи на прием"""

    title = _('Причины записи на прием')
    verbose_name = title

    add_window = edit_window = ReasonEditWindow
    model = Reason

    column_name_on_select = 'name'

    # генератор колоночных фильтров
    filter_engine_clz = ColumnFilterEngine

    F = partial(FilterByField, model)

    columns = [
        {
            'header': _('Код'),
            'data_index': 'code',
            'filter': F('code', 'code__icontains'),
            'width': 100,
        },
        {
            'header': _('Причина записи'),
            'data_index': 'name',
            'filter': F('name', 'name__icontains'),
            'width': 200,
        },
    ]

    def __init__(self):
        super(ReasonActionPack, self).__init__()
        self.replace_action('delete_action', ReasonDeleteAction())

    def extend_menu(self, menu, profile=None):
        """
        Добавление в меню "Пуск".

        .. code::
            return menu.SubMenu(
                'Расписание на прием',
                menu.Item(
                    self.title,
                    url=self.list_window_action.get_absolute_url()
                )
            )
        """
        raise NotImplementedError


class ReasonDeleteAction(ObjectDeleteAction):
    """
    Удаление причины записи на прием
    """

    def delete_obj(self, id_):
        """
        Удаление объекта по идентификатору @id_
        Перед удалением трем связи с другими таблицами
        """
        ApplicantReception = ioc.get('edureception__ApplicantReception')
        receptions = ApplicantReception.objects.filter(reason_id=id_)
        for reception in receptions:
            reception.reason = None
            reception.save()
        obj = self.parent.delete_row(id_, self.request, self.context)
        self.audit(obj)
