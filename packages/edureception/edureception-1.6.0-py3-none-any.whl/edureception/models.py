# coding: utf-8
from __future__ import (
    absolute_import,
    unicode_literals,
)

from django.db import (
    models,
)
from django.utils.translation import (
    gettext_lazy as _,
)
from future.builtins import (
    object,
)
from future.utils import (
    python_2_unicode_compatible,
)

from .base import (
    ReferenceProxy,
)


@python_2_unicode_compatible
class Reason(models.Model):
    """
    Модель 'Причины записи на прием'
    Используется для создании записи на прием
    """

    code = models.CharField(_('код'), max_length=50)
    name = models.CharField(_('наименование'), max_length=250, null=True, blank=True)

    class Meta(object):
        verbose_name = 'Причина записи на прием к специалисту'
        verbose_name_plural = 'Причины записи на прием к специалисту'

    def __str__(self):
        return self.code


class ReasonsProxy(ReferenceProxy):
    """
    Класс предназначеный для передачи в edureception
    дополнительных данных к модели Reason
    """

    model = Reason

    @staticmethod
    def get_required_fields():
        fields = [
            'name',
            'id',
        ]
        return fields
