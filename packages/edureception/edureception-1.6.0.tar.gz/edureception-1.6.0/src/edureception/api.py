# -*- coding: utf-8 -*
from __future__ import unicode_literals


def accept_reception(applicant, timetablerecord, reason):
    """
    Назначение приема специалиста посетителю
    :param applicant: заявление в школу
    :param timetablerecord: запись сетки расписания приема сотрудника
    :returns: сообщение о невозможности назначить прием, либо пустая строка
    :rtype: unicode
    """
    if timetablerecord.applicantreception_set.exists():
        if callable(timetablerecord.timetablecrontab.specialist.fullname):
            fullname = timetablerecord.timetablecrontab.specialist.fullname()
        else:
            fullname = timetablerecord.timetablecrontab.specialist.fullname
        return 'Сотрудник {0} уже ведет прием в желаемое время!'.format(
                fullname
            )

    if applicant.applicantreception_set.filter(
        timetablerecord__begin__lt=timetablerecord.end,
        timetablerecord__end__gt=timetablerecord.begin
    ).exists():
        if callable(timetablerecord.timetablecrontab.specialist.fullname):
            fullname = timetablerecord.timetablecrontab.specialist.fullname()
        else:
            fullname = timetablerecord.timetablecrontab.specialist.fullname
        return 'У {0} в это время уже назначен прием!'.format(
            fullname
        )

    reception_model = timetablerecord.applicantreception_set.model

    reception_model.objects.create(
        timetablerecord=timetablerecord,
        applicant=applicant,
        reason=reason
    )
    return ''
