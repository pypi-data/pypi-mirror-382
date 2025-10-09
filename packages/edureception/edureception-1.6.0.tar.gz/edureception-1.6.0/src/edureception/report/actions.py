# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import abc

from django.conf import settings
from educommon import ioc
from educommon.report.actions import CommonReportPack
from educommon.utils.date import get_weekdays_for_date
from m3.actions import ApplicationLogicException

from .reporter import BaseReceptionReporter
from .ui import ReportWindow

Specialist = ioc.get('edureception__Specialist')


class BaseSpecialistReceptionPrintPack(CommonReportPack):

    """Пак печати расписания."""

    report_window = ReportWindow
    reporter_class = None
    """
    Класс формирователя отчета - наследник ``reporter.BaseReceptionReporter``.

    .. code::

        reporter_class = reporter.BaseReceptionReporter
    """

    @abc.abstractproperty
    def specialist_select_pack(self):
        """
        Пак выбора специалистов для печати.

        .. code::

            ControllerCache.find_pack(BaseSpecialistSelectPrintPack)
        """

    def __init__(self):
        assert self.reporter_class, "Не указан класс формирователя отчета"
        assert issubclass(
            self.reporter_class, BaseReceptionReporter
        ), "Класс формирователя отчета {} должен быть наследником {}".format(
            self.reporter_class.__name__, BaseReceptionReporter.__name__
        )
        super(BaseSpecialistReceptionPrintPack, self).__init__()

    def declare_context(self, action):
        result = super(BaseSpecialistReceptionPrintPack, self).declare_context(
            action)
        if action is self.report_action:
            result.update(
                date_from={'type': 'date'},
                date_to={'type': 'date'},
                specialist_id={'type': 'int_or_none'}
            )
        if action is self.report_window_action:
            result.update(
                date={'type': 'date', 'default': None, 'required': False},
                specialist_id={'type': 'int_or_none', 'default': None}
            )

        return result

    def set_report_window_params(self, params, request, context):
        """Дополнение параметров окна отчёта."""
        params = super(
            BaseSpecialistReceptionPrintPack, self
        ).set_report_window_params(
            params, request, context)

        if context.specialist_id and context.date:
            week = get_weekdays_for_date(context.date)
            params['specialist'] = Specialist.objects.get(
                id=context.specialist_id)
            params['date_from'] = week[0][1]
            params['date_to'] = week[-1][1]

        params['specialist_select_pack'] = (
            self.specialist_select_pack.__class__)

        return params

    def check_report_params(self, request, context):
        """Проверка передаваемых параметров для формирования отчёта."""
        if context.date_from > context.date_to:
            raise ApplicationLogicException(
                'Неверено указаны даты! Значение в поле "Дата с" ({0}) '
                'должно быть меньше чем в поле "Дата по" ({1})'.format(
                    context.date_from.strftime(settings.DATE_FORMAT),
                    context.date_to.strftime(settings.DATE_FORMAT)
                )
            )

    def get_provider_params(self, request, context):
        """
        Преобразование request, context к словарю для создания провайдера.

        :param request:
        :param context:
        """
        params = self.context2dict(context)
        return params

    def get_builder_params(self, request, context):
        """
        Преобразование request, context к словарю для создания билдера.

        :param request:
        :param context:
        """
        return {'specialist_id': context.specialist_id}
