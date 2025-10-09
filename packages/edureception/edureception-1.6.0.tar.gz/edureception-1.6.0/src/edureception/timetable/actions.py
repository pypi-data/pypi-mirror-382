# coding: utf-8
from __future__ import unicode_literals

import abc
import datetime

from django.db.transaction import atomic
from educommon import ioc
from educommon.objectpack.actions import BaseGridPack
from edureception import providers
from edureception.api import accept_reception
from edureception.models import ReasonsProxy
from edureception.timetable.ui import (ApplicantSelectWindow,
                                       ReceptionCellEditWin,
                                       SpecialistSelectWindow, TimeTableWindow)
from m3 import actions as m3_actions
from m3_ext.ui.results import ExtUIScriptResult
from objectpack.actions import (BaseAction, ObjectPack, ObjectRowsAction,
                                ObjectSelectWindowAction)

ApplicantProxy = ioc.get('edureception__Applicant')
Specialist = ioc.get('edureception__Specialist')
ApplicantReception = ioc.get('edureception__ApplicantReception')


class BaseReceptionPack(BaseGridPack):
    """Базовый пак расписания приёма специалиста."""

    title = 'Расписание приема специалиста'
    model = None
    """
    Модель записи приема специалиста. Наследник ``.base.TTRecordBase``

    .. code::

        model = models.TimeTableRecord

    """
    _is_primary_for_model = False

    window = TimeTableWindow

    column_param_name = providers.ColumnConstructor.column_param_name
    row_id_name = 'row_id'  # не используется в данном паке

    applicant_select_win_title_fmt = "Посетители ({})"
    """
    Заголовок окна выбора посетителей для добавления на прием специалисту.
    В скобках будет указано действие: "добавить" или "изменить".


    .. code::
        applicant_select_win_title_fmt = 'Дети из заявлений ({})'
    """

    _msg_record_not_found = 'Запись расписания не найдена!'
    _msg_no_accepted_records = 'Нет назначенных приемов!'
    _msg_applicant_not_found = 'Посетитель не найден!'
    _msg_reason_not_found = 'Причина не найдена!'

    @abc.abstractproperty
    def specialist_pack(self):
        """
        Пак выбора специалистов.

        .. code::

            return ControllerCache.find_pack(SpecialistSelectPack)
        """

    @abc.abstractproperty
    def applicant_pack(self):
        """
        Пак посетителей для назначения и назначенных на прием.

        .. code::

            return ControllerCache.find_pack(ApplicantPack)
        """

    @abc.abstractproperty
    def schedule_print_pack(self):
        """
        Пак печати расписания.

        .. code::

            return ControllerCache.find_pack(SpecialistReceptionPrintPack)
        """

    def __init__(self):
        super(BaseReceptionPack, self).__init__()
        """
        экшн для редактирования ячейки расписания
        необходимо объявить в реализации класса
        .. code::
            self.edit_window_action = ReceptionEditAction()
            self.actions.append(self.edit_window_action)
        """

        # экшн данных грида
        self.rows_action = RowsAction()
        # экшн назначения посетителя на прием
        self.applicantreception_save_action = ApplicantReceptionSaveAction()
        # экшн удаления назначения посетителя на прием
        self.delete_action = ApplicantReceptionDeleteAction()

        self.actions.extend([
            self.rows_action,
            self.applicantreception_save_action,
            self.delete_action,
        ])

    def declare_context(self, action):
        result = super(BaseReceptionPack, self).declare_context(action)
        if action in (self.rows_action, self.grid_action):
            result.update(
                specialist_id={'type': 'int_or_none'},
                date={
                    'type': 'date', 'default': datetime.date.today()
                }
            )
        if action in (
            self.applicantreception_save_action,
            self.delete_action
        ):
            result['record_id'] = {'type': 'int'}

        if action in (
            self.applicantreception_save_action,
        ):
            result['is_editing'] = {'type': 'boolean'}

        if action is self.applicantreception_save_action:
            result['applicant_id'] = {'type': 'int'}
            result['reason_id'] = {'type': 'int'}

        return result

    def get_rows_url(self):
        return self.rows_action.get_absolute_url()

    def get_print_url(self):
        return self.schedule_print_pack.report_window_action.get_absolute_url()

    def create_columns(self, request, context):
        """Возвращает заголовки колонок двумерного грида."""
        return providers.ColumnConstructor(context.date).create_columns()

    def set_grid_params(self, grid, request, context):
        params = super(BaseReceptionPack, self).set_grid_params(
            grid, request, context)
        params.update(
            delete_url=self.delete_action.get_absolute_url()
        )
        return params

    def get_default_specialist(self, request, context):
        """
        Получение предвыбранного значения для поля 'Специалист'.

        .. code::

            # Пример для ЭШ
            # поиск по-умолчанию выбранного сотрудника (первого по алфавиту)
            # среди имеющих назначенные часы приема

            week = get_weekdays_for_date(_today)

            records = self.model.objects.filter(
                begin__lte=week[-1][1],
                end__gte=week[0][1],
                timetablecrontab__specialist__school=get_current_school(
                    request)
            ).order_by('timetablecrontab__specialist__person__fullname')

            # если есть право "просмотр своих" и нет права "просмотр всех"
            if self.has_perm(
                request, 'view_own'
            ) and not self.has_perm(request, 'view_all'):
                records = records.filter(
                    timetablecrontab__specialist__person__userprofile=(
                        request.user.get_profile())
                )

            if records.exists():
                specialist = records[0].timetablecrontab.specialist
            else:
                specialist = None
        """
        return None

    def get_window_params(self, request, context):
        """Передает параметры окну."""
        params = super(BaseReceptionPack, self).get_window_params(
            request, context)

        _today = datetime.date.today()

        params.update(
            read_only=not self.has_perm(request, 'edit'),
            date=_today,
            specialist_pack=self.specialist_pack.__class__,
            default_specialist=self.get_default_specialist(request, context),
            print_url=self.get_print_url()
        )
        return params

    def get_obj(self, context):
        """
        Получение объекта ``self.models``.

        по параметру self.id_param_name в контексте
        """
        return self.model.objects.get(id=getattr(context, "record_id"))

    def get_applicantreception_save_url(self):
        """Урл экшна назначения на прием / изменения приема."""
        return self.applicantreception_save_action.get_absolute_url()

    @abc.abstractmethod
    def init_provider(self, request, context):
        """
        Описание инициализации провайдера данных сетки расписания.

        .. code::

            week = get_weekdays_for_date(context.date)
            date_from, date_to = week[0][1], week[-1][1]

            provider = TimeTableProvider()
            provider.init(
                school_id=core_helpers.get_current_school(request).id,
                date_from=date_from,
                date_to=date_to,
                specialist_id=context.specialist_id)
            provider.load_data()
            return provider
        """

    def init_adapter(self, provider, request, context):
        """
        Описание инициализации адаптера данных для грида сетки расписания.
        """
        return providers.TimeTableGridAdapter(provider)

    def delete_applicant_reception(self, request, context):
        """Удаление назначения заявителя на прием."""
        try:
            timetablerecord = self.get_obj(context)
        except self.model.DoesNotExist:
            raise m3_actions.ApplicationLogicException(
                self._msg_record_not_found)

        if not timetablerecord.applicantreception_set.exists():
            raise m3_actions.ApplicationLogicException(
                self._msg_no_accepted_records)

        timetablerecord.applicantreception_set.all().delete()

    def save_applicant_reception(self, request, context):
        """Назначение на прием."""
        try:
            applicant = ApplicantProxy.model.objects.get(
                id=context.applicant_id)
        except ApplicantProxy.model.DoesNotExist:
            raise m3_actions.ApplicationLogicException(
                self._msg_applicant_not_found)

        try:
            reason = ReasonsProxy.model.objects.get(
                id=context.reason_id
            )
        except ReasonsProxy.model.DoesNotExist:
            raise m3_actions.ApplicationLogicException(
                self._msg_reason_not_found)

        try:
            timetablerecord = self.get_obj(context)
        except self.model.DoesNotExist:
            raise m3_actions.ApplicationLogicException(
                self._msg_record_not_found)

        if context.is_editing:
            # редактирование, нужно удалить предыдущие назначения приема
            timetablerecord.applicantreception_set.all().delete()

        message = accept_reception(applicant, timetablerecord, reason)
        if message:
            # не удалось
            raise m3_actions.ApplicationLogicException(message)

    def extend_menu(self, menu):
        """
        Добавление в "Пуск"

        .. code::

            return menu.SubMenu(
                'Зачисление', menu.Item(self.title, self.window_action))
        """


class RowsAction(BaseAction):

    """Экшн данных."""

    perm_code = 'view'

    def run(self, request, context):
        """
        Отображение данных по строкам.

        :rtype: PreJsonResult
        """
        provider = self.parent.init_provider(request, context)
        adapter = self.parent.init_adapter(provider, request, context)
        # Получение данных для грида: в каждой строке вместо списка словарей -
        # один словарь (ключи не пересекаются)
        result = adapter.get_rows(context.specialist_id)

        return m3_actions.PreJsonResult({'rows': result, 'total': len(result)})


class BaseReceptionEditAction(BaseAction):
    """Пак для редактирования ячейки расписания приема специалиста"""
    MSG_NOT_FOUND = "Запись не найдена"

    @abc.abstractproperty
    def reception_pack(self):
        """
        Пак расписания приема специалистов.
        .. code::

            return ControllerCache.find_pack(ReceptionPack)
        """

    def context_declaration(self):
        return {
            'record_id': {'type': 'int'},
            'is_editing': {'type': 'boolean', 'default': False}
        }

    def run(self, request, context):
        """
        Проверка и подстановка значений текущей ячейки
        :param request: Запрос
        :type request: Request
        :param context: Контекст
        :type context: dict
        :return: Окно редактирования
        :rtype: ExtUIScriptResult
        """
        try:
            record = self.reception_pack.get_obj(context)
        except self.reception_pack.model.DoesNotExist:
            raise m3_actions.ApplicationLogicException(self.MSG_NOT_FOUND)
        win = ReceptionCellEditWin()
        win.action_context = m3_actions.ActionContext(
            **{"record_id": context.record_id}
        )
        try:
            item = ApplicantReception.objects.filter(
                timetablerecord__id=context.record_id
            )[0]
        except (IndexError, AttributeError):
            pass
        else:
            win.form.from_object(item)
        win.form.url = (
            self.parent.applicantreception_save_action.get_absolute_url()
        )
        win.set_params({
            'record': record,
        })
        return ExtUIScriptResult(win)


class ApplicantReceptionSaveAction(BaseAction):

    """Экшн назначения на прием (изменения назнчения на прием)."""

    perm_code = 'add'

    @atomic
    def run(self, request, context):
        # делегирование паку
        self.parent.save_applicant_reception(request, context)
        return m3_actions.OperationResult()


class ApplicantReceptionDeleteAction(BaseAction):

    """Экшн удаления назначения заявителя на прием."""

    perm_code = 'delete'

    @atomic
    def run(self, request, context):

        # делегирование паку
        self.parent.delete_applicant_reception(request, context)

        return m3_actions.OperationResult()


class BaseApplicantPack(ObjectPack):

    """Пак списка посетителей, назначенных и для назначения на прием"""

    model = ApplicantProxy.model

    _is_primary_for_model = False

    columns = [{
        'data_index': 'fullname',
        'header': 'Ф.И.О',
        'width': 2
    }]

    column_name_on_select = 'fullname'

    MSG_NOT_FOUND = "Запись не найдена"

    select_window = ApplicantSelectWindow

    def __init__(self):
        super(BaseApplicantPack, self).__init__()
        self.replace_action("rows_action", ApplicantRowsAction())
        self.replace_action(
            "select_window_action", ApplicantSelectWindowAction()
        )
        self.assigned_rows_action = AssignedApplicantRowsAction()
        self.actions.append(self.assigned_rows_action)

    @abc.abstractproperty
    def reception_pack(self):
        """
        Пак расписания приема специалистов.

        .. code::

            return ControllerCache.find_pack(ReceptionPack)
        """

    def declare_context(self, action):
        result = super(BaseApplicantPack, self).declare_context(action)
        if action in (self.rows_action, self.assigned_rows_action):
            result['record_id'] = {'type': 'int'}
            result['is_editing'] = {'type': 'boolean', 'default': False}
        return result

    def get_rows_query(self, request, context):
        query = super(BaseApplicantPack, self).get_rows_query(
            request, context
        )
        if context.is_editing:
            # прием "переназначается на другого заявителя"
            # исключается текущий назначенный
            record = self.reception_pack.get_obj(context)
            try:
                applicant_reception = record.applicantreception_set.all()[0]
            except IndexError:
                # вызвали "Изменить" в ячейке, в кот. еще ничего не назначено
                raise m3_actions.ApplicationLogicException(self.MSG_NOT_FOUND)

            query = query.exclude(id=applicant_reception.applicant_id)

        """
        В наследнике предполагается дальнейшая фильтрация посетителей
        с учетом бизнес-логики логики системы

        .. code::

            # в ЭШ посетители - это подавшие документы на зачисление
            query = query.filter(
                school=core_helpers.get_current_school(request),
                # статус "Зарегистрировано"
                status=DECLARATION_STATUS_ACCEPT,
                # дата подачи - сегодня или раньше
                declaration__date__lte=record.begin.date()
            )

            return query.select_related('declaration').order_by(
                'declaration__fullname')
        """
        return query

    def get_list_window_params(self, params, request, context):
        params = super(BaseApplicantPack, self).get_list_window_params(
            params, request, context
        )
        if getattr(request.POST, "record_id", None):
            params["record_id"] = getattr(request.POST, "record_id", None)
        if getattr(request.POST, "is_editing", None):
            params["is_editing"] = getattr(request.POST, "is_editing", None)

        return params


class ApplicantSelectWindowAction(ObjectSelectWindowAction):
    """Экш для передачи данных контекста в окно"""

    is_select_mode = True

    def set_window_params(self):
        super(ApplicantSelectWindowAction, self).set_window_params()
        if self.request.POST.get("record_id", None):
            self.win_params["record_id"] = self.request.POST.get("record_id")
        if self.request.POST.get("is_editing", None):
            self.win_params["is_editing"] = self.request.POST.get("is_editing")


class ApplicantRowsAction(ObjectRowsAction):

    """Экшн для переопределения выдаваемых значений в гриде listWindow"""

    def get_column_data_indexes(self):
        """
        Возвращает список data_index колонок, для формирования json
        """
        res = ['__unicode__', 'fullname']
        for col in getattr(self.parent, '_columns_flat', []):
            res.append(col['data_index'])
        res.append(self.parent.id_field)
        return res


class BaseSpecialistSelectPack(ObjectPack):

    """Предок пака выбора специалиста."""

    model = Specialist
    _is_primary_for_model = False
    columns = [{
        'data_index': "fullname",
        'header': 'Ф.И.О.',
        'sortable': True,
        'searchable': True,
        'search_fields': ('fullname',),
    }]
    column_name_on_select = 'fullname'
    list_sort_order = ("fullname",)

    select_window = SpecialistSelectWindow

    def declare_context(self, action):
        result = super(BaseSpecialistSelectPack, self).declare_context(
            action)
        if action is self.rows_action:
            result['date'] = {
                'type': 'date', 'default': datetime.date.today()
            }
        return result

    @abc.abstractmethod
    def _get_timetablecrontab_query(self, request, context):
        """
        Получение записей сетки расписания в интервале выбранных дат

        .. code::

            return TimeTableCrontab.objects.filter(
                date_begin__lte=context.date,
            )
        """

    def get_rows_query(self, request, context):
        was_scheduled = self._get_timetablecrontab_query(
            request, context
        ).values_list('specialist')
        query = self.model.objects.filter(id__in=was_scheduled)

        """
        В наследнике предполагается фильтрация специалистов
        с учетом бизнес-логики логики системы

        .. code::

            query = query.filter(
                school=core_helpers.get_current_school(request),
                info_date_begin__lte=context.date,
                info_date_end__gte=context.date,
                depersonalized=False,
            )

        В том числе с учетом прав

        .. code::

            # если есть право "просмотр своих" и нет права "просмотр всех"
            if self.parent.has_perm(
                request, 'view_own'
            ) and not self.parent.has_perm(request, 'view_all'):
                query = query.filter(
                    person__userprofile=request.user.get_profile())
        """

        return query


class AssignedApplicantRowsAction(ApplicantRowsAction):
    """
    """

    def set_query(self):
        if self.context.is_editing:
            record = self.parent.reception_pack.get_obj(self.context)
            applicants_ids = record.applicantreception_set.all().values_list(
                'applicant', flat=True
            )
            self.query = self.parent.model.objects.filter(
                id__in=applicants_ids
            )
        else:
            self.query = self.parent.model.objects.none()
