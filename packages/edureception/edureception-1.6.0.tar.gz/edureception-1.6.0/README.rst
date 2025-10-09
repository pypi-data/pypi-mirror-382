Пакет для создания приложения "Прием специалиста"
=================================================

Содержит предготовые модели, действия и интерфейсы для написания продуктового приложения, позволяющего формировать расписание приема специалистов и назначать приемы посетителям

Зависимости
+++++++++++

- educommon >= 0.5.52

- пакеты платформы (указаны в зависимостях *educommon*):

    m3-objectpack==2.0.23.3

    m3-core==2.0.12.2

    m3-ui==2.0.7.13

Подключение
+++++++++++
- обновить пакет *educommon* до версии, поддерживающей *ioc* с регистрацией продуктовых моделей для расписания приемов (актуально для версии текущего пакета 0.1.0, в будущем контейнер для продуктовых моделей возможно будет перенесен)
- установить пакет pip install edureception и добавить его в ``settings.INSTALLED_APPS`` поскольку пакет содержит шаблоны
- создать и подключить продуктовое приложение, в котором:

1. Зарегистрировать продуктовые модели: Специалист, Кабинет, Посетитель.
Также необходимо передовать данные о созданых моделях для работы сервисов:
Приём специалиста, Модель расписания приёма, Модель связки 'Приём специалиста' <-> 'Посетитель'
Учреждение, Причина записи на прием, Типы документов удостоверяющих личность.

Например:

   .. code:: python

    # __init__.py

    from educommon import ioc

    from web_edu.core.teacher.models import Teacher
    from web_edu.core.office.models import Office
    from web_edu.core.declaration.models import DeclarationSchool

    # Необходимо описать import для: Учреждение, Причина записи на прием,
    # Типы документов удостоверяющих личность.

    def ioc_register():
        u"""Регистрация продуктовых моделей."""
        # специалист
        ioc.register('edureception__Specialist', Teacher)
        # кабинет
        ioc.register('edureception__Office', Office)
        # посетитель
        ioc.register('edureception__Applicant', DeclarationSchool)

        # Учреждение
        ioc.register('edureception__Organizations', Territory)
        # Причина записи на прием
        ioc.register('edureception__Reasons', Reasons)
        # Типы документов удостоверяющих личность
        ioc.register('edureception__IdentityDocumentsTypes', AlternativeTypeDocument)

        from .models import TimeTableRecord, ApplicantReception, SpecialistCronTab
        # Приём специалиста
        ioc.register('edureception__TimeTableRecord', TimeTableRecord)
        # Модель связки 'Приём специалиста' <-> 'Посетитель'
        ioc.register('edureception__ApplicantReception', ApplicantReception)
        # Модель расписания приёма
        ioc.register('edureception__SpecialistCronTab', SpecialistCronTab)

     ioc_register()

Требования к моделям:

- Специалист должен обладать аттрибутом ``fullname`` (в ином случае потребуется доопределить поведение в полях выбора из справочника, провайдер данных специалиста и метод ``_get_cell_data`` в отнаследованном от ``providers.BaseTimeTableRecordProvider`` провайдере)
- Кабинет должен обладать аттрибутами ``number``, ``location`` (в ином случае потребуется доопределить поведение в полях выбора из справочника, провайдер данных кабинетов и метод ``_get_cell_data`` в отнаследованном от ``providers.BaseTimeTableRecordProvider`` провайдере)

2. Отнаследовать абстрактные модели ``base.AbstractCrontab``, ``base.AbstractRecord``, ``base.AbstractReception``, при желании определив им менеджер аудита ``audit_log``, ``db_table``, ``verbose_name`` или подмешав продуктовую базовую модель (для ЭШ это ``BaseReplicatedModel``)

.. warning:: Описывать поля внешних ключей на продуктовые модели и на поля внутри приложения не требуется! Поля внешних ключей для моделей генерируется метаклассом ``base.TimeTableBase``

.. note:: Для модели-наследника ``base.AbstractCrontab`` требуется описать валидатор создания сетки расписания (наследник ``validators.BaseTimeTableValidator``)

3. Сгенерировать миграции приложения, добавить зависимости (от продуктовых миграций) и применить

4. Отнаследовать и доопределить провайдеры данных Специалистов, Кабинетов, Сетки расписания и Общий Провайдер данных сетки расписания

5. Отнаследовать и доопределить действия (экшны, паки), интерфейсы и провайдеры из модулей: *формирование расписания* ``scheduling``, *назначения приема* ``timetable`` и *печати расписания* согласно описанным в базовых классах абстрактным методом и абстрактным свойствам.

6. В паках необходимо дополнительно подключить проверку прав с учетом продуктовых особенностей

.. note:: Для печати расписания также требуется либо разместить xls-шаблон в приложении (по умолчанию будет поиск в ``MY_APP/templates/report/schedule_print.xls``) взяв за прототип шаблон ``edureception/templates/report/schedule_print.xls`` либо явно указать путь ``template_file_path`` до пакетного шаблона в классе репортере-наследнике ``report.reporter.BaseReceptionReporter``

6. Зарегистрировать паки приложения в ``app_meta.py``


Демо
++++

В качестве демо-приложения можно посмотреть реализацию "Расписания приема специалистов" в БАРС-Электронная Школа https://stash.bars-open.ru/projects/EDUSCHL/repos/eduschl/browse/src/web_edu/plugins/specialist_reception
