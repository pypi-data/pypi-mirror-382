# coding:utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from educommon import ioc

from future.builtins import object, str

from . import entities
from .errors import EdureceptionServiceError
from .helpers import (ONE_LEVEL_DATA, TREE_DATA, TREE_MODEL, RefsListEnum,
                      ResponseStatusEnum, convert_reception_to_timeslot,
                      find_free_slot_or_fail, find_reception_or_fail,
                      reserve_reception)

# Получаем реализованые таблиц для расписания приема
TimeTableRecord = ioc.get('edureception__TimeTableRecord')
ApplicantReception = ioc.get('edureception__ApplicantReception')
SpecialistCronTab = ioc.get('edureception__SpecialistCronTab')
ApplicantProxy = ioc.get('edureception__Applicant')
Specialist = ioc.get('edureception__Specialist')
Office = ioc.get('edureception__Office')
Organization = ioc.get('edureception__Organizations')


class ServiceProxy(object):
    """ Базовый класс для обработки ответов """

    def __init__(self, ctx, response_entity, request=None):
        self.ctx = ctx
        self.request = request
        self.response_entity = response_entity

    def build_response(self, status, message_body=None):
        response_status = self.build_response_status(status)
        message_body = message_body or {}
        message_body.update(response_status)

        return self.response_entity(**message_body)

    def build_response_status(self, status):

        if isinstance(status, dict):
            status_code = status['code']
            status_message = status['message']
        else:
            status_code = status
            status_message = ResponseStatusEnum.values[status_code]

        return {
            'error': entities.Error(
                errorDetail=entities.ErrorDetail(
                    errorCode=str(status_code),
                    errorMessage=status_message
                )
            )
        }

    def process(self):
        try:
            return self.do_process()
        except EdureceptionServiceError as e:
            if e.message:
                status = {
                    'code': ResponseStatusEnum.INTERNAL_ERROR,
                    'message': e.message
                }
            else:
                status = ResponseStatusEnum.INTERNAL_ERROR

            return self.build_response(status)

    def do_process(self):
        raise NotImplemented


class ApplyFilterRequest(object):
    """ Класс для работы с фильтрацией """

    def prepare_query(self, query):
        return query


class GetSlotsProxy(ApplyFilterRequest, ServiceProxy):
    """ Метод getSlots - Запросить свободные слоты времени. """

    def get_slots(self):
        """
        Метод выборки слотов времени доступных для бронирования
        :return: Возвращаем список данных
        :rtype: list
        """

        meta = Organization.model._meta if hasattr(
            Organization, 'model') else Organization._meta

        office_ids = Office.objects.filter(**{
            meta.model_name: self.request.organizationId
        }).values_list("id", flat=True)

        specialists = SpecialistCronTab.objects.filter(
            office_id__in=office_ids)

        time_slot_array = []
        for specialist in specialists:
            slots = TimeTableRecord.objects.filter(
                timetablecrontab=specialist
            )
            slots = self.prepare_query(slots)

            for obj in slots:

                applicant_reception = (
                    ApplicantReception.objects.filter(
                        timetablerecord=obj
                    ).count()
                )

                if applicant_reception == 0:
                    time_slot_array.append(
                        entities.SlotData(
                            slotId="{0}".format(obj.id),
                            organizationId="{0}".format(
                                self.request.organizationId
                            ),
                            areaId="{0}".format(specialist.office_id),
                            visitTime=obj.begin,
                            duration="{0}".format(specialist.duration),
                        )
                    )

        return {
            "slots": entities.SlotDataList(
                TimeSlot=time_slot_array
            )
        }

    def do_process(self):
        """
        Создание списка свободных слотов времени
        :return: Возвращаем сформированый объект ответа на запрос
        :rtype: getSlotsEntityResponse
        """
        slots_list = self.get_slots()
        return self.build_response(ResponseStatusEnum.SUCCESS, slots_list)


BLIND_REQUEST_SLOT = 'blind_request'


class BookProxy(ServiceProxy):
    """
    Прокси для метода services.bookRequest
    Создает записи о приеме у специалиста
    """

    def build_blind_applicant_reception(self, applicant):
        """
        Резервирует первый доступный слот приема за заявителем на уровне базы
        данных.
        :param applicant: заявитель.
        :return: Зарезервированая запись.
        :rtype: ApplicantReception
        """
        # TODO: Померять и заоптимизировать. Возможно здесь будет медленно.
        reserved_timetablerecord_ids = ApplicantReception.objects.filter(
            status=ApplicantReception.STATUS_APPLIED
        ).values_list('timetablerecord_id', flat=True)

        free_slots = TimeTableRecord.objects.exclude(
            id__in=reserved_timetablerecord_ids
        )

        if not free_slots.exists():
            raise EdureceptionServiceError('Нет свободных слотов')

        return reserve_reception(self.request.bookId, applicant, free_slots[0])

    def build_applicant_reception(self, slot_id, applicant):
        """
        Резервирует слот приема за заявителем на уровне базы данных.
        :param slot_id: id слота на запись у специалиста.
        :param applicant: заявитель.
        :return: Зарезервированая запись.
        :rtype: ApplicantReception
        """
        time_table_record = find_free_slot_or_fail(slot_id)

        return reserve_reception(
            self.request.bookId, applicant, time_table_record
        )

    def do_process(self):
        """
        Резарвирует запрошеные слоты приема за заявителем.
        :return: Spyne объект о результатах резервирования.
        :rtype: BookResponse.
        """
        slot_id = self.request.slotId
        applicant = ApplicantProxy.get_or_create(
            last_name=self.request.lastName,
            first_name=self.request.firstName,
            middle_name=self.request.middleName,
            document=self.request.userDoc.Document,
            declarant_type=self.request.declarantType,
            email=self.request.email,
            mobile_phone=self.request.mobilePhone,
            organization_ids=self.request.organizationId,
        )

        if slot_id == BLIND_REQUEST_SLOT:
            reception = self.build_blind_applicant_reception(applicant)
        else:
            reception = self.build_applicant_reception(slot_id, applicant)

        slot = convert_reception_to_timeslot(reception)

        status = entities.StatusData(
            statusCode='{0}'.format(ResponseStatusEnum.SUCCESS),
            statusMessage=ResponseStatusEnum.values[ResponseStatusEnum.SUCCESS]
        )

        book_response = {
            'bookId': reception.book_id,
            'esiaId': '{0}'.format(applicant.id),
            'timeSlot': slot,
            'status': status
        }

        return self.build_response(ResponseStatusEnum.SUCCESS, book_response)


class GetRefsListProxy(ServiceProxy):
    """
    Метод getRefsList - Метод позволяет ЕПГУ получать информацию о списке
    справочников, имеющихся в системе. Используется для первоначального
    наполнения базы справочной информации ЕПГУ и отображения на этапе
    конфигурирования услуги.
    """

    def get_refsList(self):
        """
        Метод выборки справочников
        :return: Возвращаем список данных
        :rtype: list
        """
        refs_list = RefsListEnum()
        refs_data_array = list()
        for name in refs_list.values:
            refs_data_array.append(
                entities.RefInfoData(
                    name=name,
                    title=refs_list.values[name]["title"],
                    kind=refs_list.values[name]["kind"],
                )
            )

        return {
            "refsList": entities.RefsDataList(
                RefInfo=refs_data_array
            )
        }

    def do_process(self):
        """
        Создание списка справочников
        :return: Возвращаем сформированый объект ответа на запрос
        :rtype: getRefsListEntityResponse
        """
        refs_list = self.get_refsList()
        return self.build_response(ResponseStatusEnum.SUCCESS, refs_list)


class GetRefAttributesListProxy(ServiceProxy):
    """
    Метод GetRefAttributesList позволяет получать информацию об атрибутах
    конкретного справочника. Используется для первоначального наполнения базы
    справочной информации ЕПГУ и отображения на этапе конфигурирования услуги.
    В рамках услуги "Запись на прием к специалисту" требуется получение
    атрибутов справочника "Учреждение" и "Причина записи на прием" и
    "Тип документа, удостоверяющего личность".
    """

    def get_refsAttributes(self):
        """
        Метод выборки справочников и их полей
        :return: Возвращаем список данных
        :rtype: list
        """
        refs_list = RefsListEnum()
        refs_data_fields_array = list()

        try:
            required_refs = self.request.refNames
        except AttributeError:
            raise EdureceptionServiceError(
                "Не указаны справочники для передачи данных"
            )
        else:
            if not required_refs:
                raise EdureceptionServiceError(
                    "Не указаны справочники для передачи данных"
                )

        for name in required_refs:
            try:
                fields = refs_list.values[name]["fields"]
            except KeyError:
                raise EdureceptionServiceError(
                    "Не найден справочник по указанной мнемоники"
                )

            for field in fields:
                refs_data_fields_array.append(
                    entities.RefAttributeInfo(
                        refName=name,
                        name=field["name"],
                        title=field["title"],
                        type=field["type"],
                        attrRefName=field["attrRefName"],
                        allowFiltering=field["allowFiltering"]
                    )
                )

        return {
            "refAttributesList": entities.RefAttributesList(
                RefAttributeInfo=refs_data_fields_array
            )
        }

    def do_process(self):
        """
        Создание списка полей справочников
        :return: Возвращаем сформированный объект ответа на запрос
        :rtype: getRefAttributesListEntityResponse
        """
        refs_attr = self.get_refsAttributes()
        return self.build_response(ResponseStatusEnum.SUCCESS, refs_attr)


class GetBookingStatusProxy(ServiceProxy):

    def do_process(self):
        reception = find_reception_or_fail(
            self.request.bookId,  self.request.esiaId
        )

        booking_status = {
            'bookId': self.request.bookId,
            'esiaId': self.request.esiaId,
            'status': '{0}'.format(reception.status),
            'timeSlot': convert_reception_to_timeslot(reception)
        }

        return self.build_response(ResponseStatusEnum.SUCCESS, booking_status)


class GetRefItemsListProxy(ServiceProxy):
    """
    Метод GetRefItemsList позволяет получать информацию о данных справочника.
    Используется для первоначального наполнения базы справочной
    информации ЕПГУ, а также для последующей синхронизации.
    """
    # Поля по которым сортировать используется
    # при форимрования запроса .order_by(*ordering)
    ordering = []

    # Список атрибутов значение которых необходимо вернуть
    attributes = []

    # Мнемоника запрашиваемого справоника
    name_ref = ""

    # Общие количесто возвращаемых элементов
    total_count = 0

    def get_refs_items_list(self):
        """
        Метод получения данных справочника
        :return: Возвращаем список данных
        :rtype: list
        """
        refs_list = RefsListEnum()

        self.name_ref = self.request.refName
        parent_id = self.request.parentRefItemValue
        level = self.request.treeFiltering
        self.ordering = self.request.orderBy
        self.attributes = self.request.selectAttributes

        if (
            self.name_ref not in refs_list.relationship or
            not hasattr(refs_list.relationship[self.name_ref], 'model')
        ):
            raise EdureceptionServiceError(
                "Данной {0} мнемоники справочника не существует".format(
                    self.name_ref
                )
            )

        ref_class = refs_list.relationship[self.name_ref]
        ref = ref_class()

        # Если справочник иерархичный то вывод данных
        # должен включать в себе иерархию
        ref_options = refs_list.values[self.name_ref]
        if ref_options["kind"] == TREE_MODEL:
            data_items_list = self._get_hierarchic_data(
                ref, ref_options, parent_id, level)
        else:
            data_items_list = list()
            for obj in ref.get_data(self.ordering):
                self.total_count += 1
                item_dict = self._create_item_dict(obj, ref)
                data_items_list.append(item_dict)

        return {
            "totalItems": str(self.total_count),
            "items": data_items_list,
        }

    def _get_hierarchic_data(self, ref, ref_options, parent_id, level):
        """
        Формируем древовидные данные в зависимости от запроса.
        Может демонстрировать дерево целиком.
        Или один уровень. Так же можно вывести потомков конкретного родителя
        :param ref: модель для запросов
        :type ref: models.Model или m3.db.BaseEnumerate
        :param ref_options: Описания свойст справочника
        :type ref_options: edureception.webservice.helpers.RefsListEnum
        :param parent_id: Индентификатор родителя
        :type parent_id: int
        :param level: Описание сколько уровней вложенности брать
        :type level: str
        :return:
        """
        data_items_list = list()
        self_reference_field = ref_options["self_reference_field"]

        if parent_id:
            # Если есть индентификатор родителя то
            # выводим дерево наследников
            if level == ONE_LEVEL_DATA:
                data_items_list = self._get_obj_ids(
                    self_reference_field, ref, parent_id, max_level=0
                )
            elif level == TREE_DATA:
                data_items_list = self._get_obj_ids(
                    self_reference_field, ref, parent_id
                )
        else:
            if level == ONE_LEVEL_DATA:
                data_items_list = self._get_obj_ids(
                    self_reference_field, ref, parent_id=None, max_level=0
                )
            elif level == TREE_DATA:
                data_items_list = self._get_obj_ids(
                    self_reference_field, ref, parent_id=None
                )
        return data_items_list

    def do_process(self):
        """
        Создание списка полей справочников
        :return: Возвращаем сформированый объект ответа на запрос
        :rtype: getRefAttributesListEntityResponse
        """
        refs_attr = self.get_refs_items_list()
        return self.build_response(ResponseStatusEnum.SUCCESS, refs_attr)

    def _get_obj_ids(self, attr_parent_name, ref, parent_id,
                     level=0, max_level=10):
        """
        Рекурсивный метод для получение дерева справочника
        :param attr_parent_name: атрибут в котором хранится связь
        :type: str
        :param ref: модель для запросов
        :type ref: models.Model
        :param parent_id: индентификатор родительского элемента
        :type: str
        :param level: текущий уровень
        :type: int
        :param max_level: максимальный уровень
        :type: int
        :return: Массив элементов значений справочника
        :rtype: list(entities.RefItem, ...)
        """

        # проверка на уровень.
        # По умолчанию 10 чтобы не улететь в бессконечность
        if level > max_level:
            return

        if parent_id:
            param = {
                attr_parent_name: parent_id
            }
        else:
            param = {
                "{0}__isnull".format(attr_parent_name): True
            }

        result = list()

        for obj in ref.model.objects.filter(**param).order_by(*self.ordering):
            self.total_count += 1
            item_dict = self._create_item_dict(obj, ref)
            item_dict.children = (
                self._get_obj_ids(attr_parent_name, ref, obj.id, level + 1)
            )
            result.append(item_dict)

        return result

    def _create_item_dict(self, obj, ref):
        """
        Создание элемента значения справочника
        :param obj: объект полученный из модели
        :type obj: object(models.Model)
        :param ref: модель для запросов
        :type ref: models.Model или m3.db.BaseEnumerate
        :return: элемент справочника
        :rtype: entities.RefItem
        """

        attr_list = list()

        # Если атрибуты не указанны в запросе то берем атрибуты из свойств
        # справочника
        attributes = ref.required_fields
        if self.attributes:
            attributes = self.attributes

        for attr in attributes:
            data = ref.get_attribute_data(obj, attr)
            if not isinstance(data, (str, bytes)):
                data = str(data)
            attr_list.append(
                entities.RefAttribute(
                    name=attr,
                    value=data
                )
            )
        return entities.RefItem(
            parentItem=self.name_ref,
            attributes=attr_list,
            fields=entities.RefItemField(
                itemName="empty",
                title="empty"
            )
        )


class UpdateBookingDetailsProxy(ServiceProxy):
    """
    Прокси для метода services.updateBookingDetails
    Вносит изменения в поданную ранее заявку на бронирование.
    """
    def do_process(self):
        """
        Находим слот на прием указаный в запросе. Удаляем старую заявку.
        Создаем новую заявку для слота указанного в запросе.
        :return: Spyne объект о результатах резервирования.
        :rtype: entities.UpdateBookingDetailsResponse.
        """
        reception = find_reception_or_fail(
            self.request.bookId,  self.request.esiaId
        )

        timetable_slot = find_free_slot_or_fail(self.request.timeSlot.slotId)

        # В ГТН delete не удаляет инстанции сразу.  А book_id - уникальное
        # поле. Занулаем book_id, чтобы создать ApplicantReception c таким
        # же book_id
        reception.book_id = None
        reception.save()
        reception.delete()

        reserve_reception(
            self.request.bookId, reception.applicant, timetable_slot
        )

        update_response = {
            'bookId': self.request.bookId,
            'esiaId': self.request.esiaId,
        }

        return self.build_response(ResponseStatusEnum.SUCCESS, update_response)


class CancelBookingProxy(ServiceProxy):
    """
    Прокси для метода services.cancelBookingRequest
    Отменяет запись о приеме у специалиста
    """

    def do_process(self):
        """
        Отменяет зарезервированую запись.
        :return: Spyne объект о результатах резервирования.
        :rtype: entities.CancelBookingResponse.
        """

        reception = find_reception_or_fail(
            self.request.bookId,  self.request.esiaId
        )

        reception.status = ApplicantReception.STATUS_CANCELED
        reception.save()

        cancel_response = {
            'bookId': self.request.bookId,
            'esiaId': self.request.esiaId,
            'status': '{0}'.format(ApplicantReception.STATUS_CANCELED),
        }

        return self.build_response(ResponseStatusEnum.SUCCESS, cancel_response)
