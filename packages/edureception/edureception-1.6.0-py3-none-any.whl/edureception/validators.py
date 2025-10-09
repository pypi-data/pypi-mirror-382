# coding: utf-8
from __future__ import unicode_literals

import datetime

from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from educommon import ioc

from future.builtins import object
from future.utils import iteritems


class BaseTimeTableValidator(object):

    """Базовый валидатор создания сетки расписания."""

    # список ошибок
    errors = None

    # перечень вызываемых валидаций в порядке их вызова
    ALL = [
        'validate_config',
        'validate_period_length',
        'validate_has_schedule'
        # 'yet_another_method',
    ]

    _msg_no_days_selected = (
        'небходимо выбрать хотя бы один день для формирования!')

    _msg_already_exist = (
        'специалисту {0} уже назначен прием в интервале {1} - {2}!')
    _msg_bad_period_len = (
        'превышено максимальная продолжительность периода ({0}, указано: {1})'
    )
    _msg_no_weekdays = (
        '{0}: для периодичности "Ежемесячно"'
        ' необходимо выбрать хотя бы один день!'
    )
    _msg_bad_time = 'некорректно указано время приема ({0})'
    _msg_bad_duration = (
        'суммарное время приемов за день ({0}) не должно быть меньше или '
        'не кратным значению, указанному в поле "Продолжительность (мин.)"')
    _msg_has_schedule = 'у специалиста {0} на даты {1} уже назначены приемы.'

    def __init__(self, timetable):
        self.errors = []
        # флаг о том, что дальше не требуется производить проверки
        self._need_stop = False

        self._timetable = timetable
        self._dates = sorted(self._timetable.iterdates())
        self._specialist = self._timetable.specialist
        self._fullname = self._specialist.fullname()

    def __call__(self):
        """
        Основной метод валидации.

        Вызывает поочереди валидаторы из self.ALL
        по аналогии с django.core.validators
        :raise: ValidationError
        """

        for validate_name in self.ALL:
            if not self._need_stop:
                getattr(self, validate_name)()

        if self.errors:
            raise ValidationError({NON_FIELD_ERRORS: self.errors})

    def stop_validation(self):
        """Установить флаг о том, что остальные проверки делать не нужно."""
        self._need_stop = True

    def validate_config(self):
        """
        Проверки полей формы, кратности продолжительности и указанного времени.
        """

        msgs = []  # локальные ошибки
        no_data = True  # флаг, что вообще нет данных (ни один день не выбран)
        weekdays = dict(self._timetable.WEEKDAYS)
        duration = self._timetable.get_timedelta_duration()
        strptime = lambda time: datetime.datetime.strptime(
            time, self._timetable.TIME_FORMAT)

        for day_idx, data in iteritems(self._timetable.config):
            if not data:
                continue

            day_name = weekdays[day_idx]
            no_data = False
            if not data['begin'] or not data['end']:
                # время начала/окончания не указано
                msgs.append(self._msg_bad_time.format(day_name))
                continue

            begin, end = strptime(data['begin']), strptime(data['end'])

            if end <= begin:
                msgs.append(self._msg_bad_time.format(day_name))
                continue

            if not data['days'] and (
                self._timetable.period_type == self._timetable.PERIOD_MONTH
            ):
                # выбран период "Ежемесячно", но не выбрана ни одна неделя
                msgs.append(
                    self._msg_no_weekdays.format(day_name))
                continue

            # проверка продолжительности и времени
            quotient, remainder = divmod(
                (end - begin).seconds, duration.seconds)
            # если нет целой части - значит duration < end - begin
            # либо есть остаток
            if not quotient or remainder:
                msgs.append(self._msg_bad_duration.format(day_name))

        if no_data:
            msgs.append(self._msg_no_days_selected)

        if msgs:
            self.errors.extend(msgs)
            self.stop_validation()

    def validate_period_length(self):
        """Проверка продолжительности периода"""
        max_period_length = self._timetable.MAX_PERIOD_LENGTH[
            self._timetable.period_type]
        if self._timetable.period_length > max_period_length:
            self.errors.append(
                self._msg_bad_period_len.format(
                    max_period_length, self.period_length))
            self.stop_validation()
            return

        """
        Пример дополнительных проверок:
        Для ЭШ требуется дополнительно проверять вхождение в период обучения

        .. code::

            period_at_start = Period.get_for_date(self._dates[0])
            period_at_end = Period.get_for_date(self._dates[-1])

            if not period_at_start or not period_at_end:
                self.errors.append(self._msg_no_period.format(
                    self._dates[0].strftime(settings.DATE_FORMAT),
                    self._dates[-1].strftime(settings.DATE_FORMAT),
                ))
                self.stop_validation()
            elif period_at_start.id != period_at_end.id:
                self.errors.append(self._msg_different_periods.format(
                    self._dates[-1].strftime(settings.DATE_FORMAT),
                    period_at_start.display()
                ))
                self.stop_validation()
        """

    def validate_has_schedule(self):
        """Если есть назначенные специалисту приемы хотя бы в одну из дат."""
        cur_dates = set(self._dates)

        CrontabModel = ioc.get('edureception__SpecialistCronTab')
        for crontab in CrontabModel.objects.filter(
                specialist=self._specialist
        ).exclude(
            id=self._timetable.id
        ):
            intersect = cur_dates & set(crontab.iterdates())
            if intersect:
                self.errors.append(
                    self._msg_has_schedule.format(
                        self._fullname,
                        ', '.join(
                            d.strftime(settings.DATE_FORMAT) for d in intersect
                        )
                    )
                )

    """
    Пример дополнительной валидации исходя из продуктовой бизнес-логики

    .. code::

    def validate_specialist(self):
        u\"""Проверка не уволен ли сотрудник.\"""

        date_end = self._dates[-1]
        if self._specialist.info_date_end.date() < date_end:
            self.errors.append(self._msg_specialist_out_dates.format(
                self._fullname,
                self._specialist.info_date_end.strftime(settings.DATE_FORMAT)
            ))
    """
