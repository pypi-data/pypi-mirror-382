# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import abc
import os
from collections import defaultdict

from django.conf import settings
from django.utils.functional import cached_property
from educommon.report import AbstractReportBuilder, BaseProviderAdapter
from educommon.report.reporter import SimpleReporter
from educommon.utils.date import WEEKDAYS_DICT
from simple_report.interface import ISpreadsheetSection as interface

from future.builtins import range, zip
from future.utils import iteritems

from ..providers import BaseTimeTableProvider


class BaseTimeTableReportAdapter(BaseProviderAdapter):

    """Адаптирует данные расписания для формирования отчета."""

    # количество столбцов расписания на одной странице А4
    # соответствует кол-ву дней в условной неделе
    _columns_count = 7

    # кол-во строк расписания (без учета заголовка)
    # которые должны выводиться на одну страницу А4
    _max_rows_count = 7

    # информация разбиении на условные недели
    chunks_data = None

    def __init__(self, provider):
        super(BaseTimeTableReportAdapter, self).__init__(provider)
        self.chunks_data = defaultdict(dict)

    @staticmethod
    def chunks(iterable, chunk_size):
        """
        Разбиение списка на списки размеров по chunk_size.

        :param list iterable: список, который разбивается
        :param int chunk_size: размер разбиения

        """
        for index in range(0, len(iterable), chunk_size):
            yield iterable[index: index + chunk_size]

    @property
    def data(self):
        """Данные для отчета в виде словаря."""

        data = defaultdict(dict)

        for specialist, by_dates in iteritems(self.provider.timetable_data):
            specialist_data = {}

            for chunk_idx, chunk in enumerate(
                self.chunks(sorted(by_dates.keys()), self._columns_count)
            ):

                self.chunks_data[specialist][chunk_idx] = chunk
                # данные за условную неделю
                chunk_data = []
                # макс. кол-во строк за 7дней условной недели приема
                max_day_reception_len = max(
                    len(by_dates[date]) for date in chunk)

                # цикл по датам условной недели
                # дополнение до равного количества записей в каждом столбце
                # значениями None
                for date in chunk:
                    col_data = [cell for _, cell in by_dates[date]]
                    diff = max_day_reception_len - len(col_data)
                    col_data.extend([None, ] * diff)
                    chunk_data.append(col_data)

                # транспонирование, данные теперь - по строкам
                # а строки разбиваются на порции по self._max_rows_count строк
                # (чтобы уместить на листе А4)
                specialist_data[chunk_idx] = self.chunks(
                    list(zip(*chunk_data)), self._max_rows_count)

            data[specialist] = specialist_data
        return data

    @abc.abstractproperty
    def unit_code(self):
        """
        Краткое имя учреждения в рамках которого формируется расписание.

        .. code::

            return School.objects.get(id=self.provider._school_id).code
        """

    @property
    def specialist_name(self):
        """Имя специалиста, для которого было сформировано расписание"""
        return self.provider._specialists_provider.data[
            self.provider._specialist_id]['fullname']


class ReportBuilder(AbstractReportBuilder):

    """Билдер отчета-печати расписания."""

    # секции
    HEADER = 'header'
    TABLE_HEADER = 'day_header'
    CELL = 'cell'
    EMPTY_ROW = 'empty_row'
    EMPTY_CELL = 'empty_cell'

    # формат данных в ячейке
    # TODO вынести на клиент
    _cell_format = '{0} - {1}\n{2}\n{3}'

    @cached_property
    def _no_reception(self):
        """Сообщение в свободной от приёма ячейке."""
        return self.adapter.provider._timetable_provider.model.NO_RECEPTION

    def __init__(self, provider, adapter, report, params):

        self.adapter = adapter(provider)
        self.report = report
        self.specialist_id = params['specialist_id']

    def _set_sections(self):
        self.header = self.report.get_section(self.HEADER)
        self.table_header = self.report.get_section(self.TABLE_HEADER)
        self.cell = self.report.get_section(self.CELL)
        self.empty_row = self.report.get_section(self.EMPTY_ROW)
        self.empty_cell = self.report.get_section(self.EMPTY_CELL)

    def _format_cell(self, cell_data):
        """
        Форматирование значений ячеек в столбце.

        :param list datedata: список данных ячеек в одной колонке
        """
        if not cell_data:
            return self._no_reception
        else:
            return self._cell_format.format(
                cell_data['begin'],
                cell_data['end'],
                'каб.%s (%s)' % (
                    cell_data['office'].get('number', ''),
                    cell_data['office'].get('location', '')
                ),
                cell_data['fullname'] or ' \n'
            )

    def build(self):
        self._set_sections()

        # пока печатает только для одного сотрудника
        data = self.adapter.data[self.specialist_id]
        chunks = self.adapter.chunks_data[self.specialist_id]

        max_rows = self.adapter._max_rows_count

        for chunk_idx, column_chunk_data in iteritems(data):
            dates = chunks[chunk_idx]

            for row_chunks in column_chunk_data:

                self._flush_header()
                self._flush_thead(dates)
                self._flush_rows(row_chunks)

                rows_count = len(row_chunks)
                if rows_count < max_rows:
                    for _ in range(0, max_rows - rows_count):
                        self._flush_empty_cell()
                else:
                    self._flush_empty_row()

        self._set_page_settings()

    def _flush_header(self):
        # заголовок расписания
        self.header.flush({
            'unit_name': self.adapter.unit_code,
            'specialist_name': self.adapter.specialist_name
        }, interface.VERTICAL)

    def _flush_thead(self, dates):
        # заголовок таблицы
        for col_idx, date in enumerate(dates):

            self.table_header.flush({
                'day_name': WEEKDAYS_DICT[date.weekday()],
                'date': date.strftime(settings.DATE_FORMAT)
            }, interface.VERTICAL if col_idx == 0 else interface.HORIZONTAL)

    def _flush_rows(self, row_chunks):
        # строки расписания
        for row in row_chunks:
            for col_idx, cell_data in enumerate(row):

                self.cell.flush({
                    'value': self._format_cell(cell_data),
                }, interface.VERTICAL if col_idx == 0 else interface.HORIZONTAL
                )

    def _flush_empty_row(self):
        # пустая строка (футер)
        self.empty_row.flush({}, interface.VERTICAL)

    def _flush_empty_cell(self):
        # пустая ячейка, когда порция строк не кратна self._max_rows_count
        self.empty_cell.flush({}, interface.VERTICAL)

    def _set_page_settings(self):
        # параметры печати
        wtsheet = self.report.sheets[0].writer.wtsheet
        wtsheet.portrait = False


class BaseReceptionReporter(SimpleReporter):

    """Построитель отчета для печати расписания приема специалистов."""

    template_file_path = os.path.join(
        './..', 'templates', 'report', 'schedule_print')
    builder_class = ReportBuilder

    data_provider_class = None
    """
    Класс провайдера данных - наследник BaseTimeTableProvider

    .. code::

        data_provider_class = BaseTimeTableProvider
    """
    adapter_class = None
    """
    Класс адаптера для провайдера данных - наследник BaseProviderAdapter

    .. code::

        data_provider_class = BaseProviderAdapter
    """
    def __init__(self, provider_params, builder_params):
        assert issubclass(self.adapter_class, BaseProviderAdapter)
        assert issubclass(self.data_provider_class, BaseTimeTableProvider)
        super(BaseReceptionReporter, self).__init__(
            provider_params, builder_params)
