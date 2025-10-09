# coding:utf-8
from __future__ import unicode_literals

from spyne.model.complex import Array
from spyne.model.complex import ComplexModel
from spyne.model.complex import SelfReference
from spyne.model.enum import Enum
from spyne.model.primitive import Boolean, Date, DateTime, Integer, Unicode

# from future.utils import with_metaclass

CONFIG_NAMESPACE = 'http://epgu.rtlabs.ru/equeue/ws/'


# region Базовые примитивные типы
class NotBlankUnicode(Unicode):
    class Attributes(Unicode.Attributes):
        nillable = False
        min_occurs = 0


class BlankUnicode(Unicode):
    class Attributes(Unicode.Attributes):
        nillable = True
        min_occurs = 0


class NotBlankDate(Date):
    """Класс для обязательных полей c датой"""
    class Attributes(Date.Attributes):
        nillable = False
        min_occurs = 0


class NotBlankDateTime(DateTime):
    """Класс для обязательных полей c датой и временем"""
    class Attributes(DateTime.Attributes):
        nillable = False
        min_occurs = 0



class Status(NotBlankUnicode):
    class Annotations(Unicode.Annotations):
        doc = 'Статус'


class ComplexModelWithNamespace(ComplexModel):
    """
    Для перегрузки пространства имен
    """
    __namespace__ = CONFIG_NAMESPACE
# endregion


# region Основная информация о запросе
class Reason(ComplexModelWithNamespace):
    code = NotBlankUnicode
    name = NotBlankUnicode

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Назначение обследования'


class Municipality(ComplexModelWithNamespace):
    code = Unicode.customize(nillable=False, min_occurs=1, max_occurs=1)
    name = NotBlankUnicode

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = (
            'Блок, содержащий информацию об организации,'
            'в которую подается заявление'
        )


class Organization(ComplexModelWithNamespace):

    code = Unicode.customize(nillable=False, min_occurs=1, max_occurs=1)
    name = NotBlankUnicode

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит информацию о организации'


class Comment(NotBlankUnicode):
    class Annotations(Unicode.Annotations):
        doc = 'Дополнительная информация о запросе'
# endregion


# region Базовые классы запроса и ответа
class BaseEntityRequest(ComplexModelWithNamespace):
    """
    Базовый класс запроса.
    """

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Базовая информация о запросе'


class BaseEntityResponse(ComplexModelWithNamespace):
    """
    Базовый класс ответа.
    """
    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Базовая информация о ответе'


class Document(ComplexModelWithNamespace):
    docType = BlankUnicode
    docSeries = BlankUnicode
    docNumber = BlankUnicode
    issueDate = Date
    validDate = Date
    issuedBy = BlankUnicode
    issueDept = BlankUnicode

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит описание документа'


class DocumentType(ComplexModelWithNamespace):
    Document = Document

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит секцию документа'



class SimplePredicate(ComplexModelWithNamespace):
    attributeName = BlankUnicode
    condition = BlankUnicode
    checkAllValues = BlankUnicode
    value = BlankUnicode

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит описание фильтрации по атрибуту'


class LogicalUnionPredicate(ComplexModelWithNamespace):
    unionKind = BlankUnicode
    subs = SimplePredicate.customize(
        max_occurs='unbounded', min_occurs=0
    )

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит состовной список фильтрации'


class Predicate(ComplexModelWithNamespace):
    simple = SimplePredicate
    union = LogicalUnionPredicate

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит условияя фильтрации'


class ErrorDetail(ComplexModelWithNamespace):
    errorCode = NotBlankUnicode
    errorMessage = BlankUnicode

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит описание ошибки'


class FieldError(ComplexModelWithNamespace):
    fieldName = BlankUnicode
    errorDetail = ErrorDetail

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит описание ошибочных полей'


class Error(ComplexModelWithNamespace):
    errorDetail = ErrorDetail
    fieldErrors = Array(FieldError)

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит описание текущего статуса'

# endregion


# region getSlotsEntityRequest

class getSlotsEntityRequest(BaseEntityRequest):
    organizationId = NotBlankUnicode
    userType = NotBlankUnicode
    filter = Predicate
    attributes = BlankUnicode

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит запрос на выдачу незанятых слотов времени'

# endregion


# region getSlotsEntityResponse

class SlotData(ComplexModelWithNamespace):
    slotId = Unicode.customize(nillable=False, min_occurs=1, max_occurs=1)
    organizationId = NotBlankUnicode
    areaId = NotBlankUnicode
    visitTime = DateTime
    duration = NotBlankUnicode

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит информацию о свободном слоте'


class SlotDataList(ComplexModelWithNamespace):
    TimeSlot = SlotData.customize(max_occurs='unbounded', min_occurs=0)

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит список слотов'


class getSlotsEntityResponse(ComplexModelWithNamespace):
    slots = SlotDataList
    error = Error

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит ответ на запрос о свободных слотов времени'

# endregion


# region getRefsListEntityResponse
class RefInfoData(ComplexModelWithNamespace):
    name = NotBlankUnicode
    title = NotBlankUnicode
    kind = NotBlankUnicode

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит информацию о справочнике'


class RefsDataList(ComplexModelWithNamespace):
    RefInfo = RefInfoData.customize(max_occurs='unbounded', min_occurs=0)

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит список справочников'


class getRefsListEntityResponse(ComplexModelWithNamespace):
    refsList = RefsDataList
    error = Error

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Ответ содержит информацию о справочниках расписания на прием'
# endregion


# region getRefAttributesListEntityRequest
class getRefAttributesListEntityRequest(BaseEntityRequest):
    refNames = NotBlankUnicode.customize(max_occurs='unbounded', min_occurs=0)

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит запрос на выдачу атрибутов справочника'
# endregion


# region getRefAttributesListEntityResponse
class RefAttributeInfo(ComplexModelWithNamespace):
    refName = NotBlankUnicode
    name = NotBlankUnicode
    title = NotBlankUnicode
    type = NotBlankUnicode
    attrRefName = BlankUnicode
    allowFiltering = Boolean

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит информацию о атрибутах справочников'


class RefAttributesList(ComplexModelWithNamespace):
    RefAttributeInfo = RefAttributeInfo.customize(
        max_occurs='unbounded', min_occurs=0
    )

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит список атрибутов справочников'


class getRefAttributesListEntityResponse(ComplexModelWithNamespace):
    refAttributesList = RefAttributesList

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Ответ содержит информацию о атрибутах справочников'
# endregion


# region getRefItemsListRequest
class getRefItemsListEntityRequest(BaseEntityRequest):
    refName = NotBlankUnicode
    parentRefItemValue = BlankUnicode
    treeFiltering = NotBlankUnicode
    selectAttributes = BlankUnicode.customize(
        max_occurs='unbounded', min_occurs=0
    )
    filter = Predicate
    orderBy = BlankUnicode.customize(
        max_occurs='unbounded', min_occurs=0
    )
    pageNum = NotBlankUnicode
    pageSize = NotBlankUnicode
    version = BlankUnicode

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит запрос на выдачу незанятых слотов времени'
# endregion


# region getRefItemsListResponse
class RefAttribute(ComplexModelWithNamespace):
    name = NotBlankUnicode
    value = NotBlankUnicode

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит информацию значения атрибутов записи'


class RefItemField(ComplexModelWithNamespace):
    itemName = NotBlankUnicode
    title = NotBlankUnicode

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит информацию значения атрибутов записи'


class RefItem(ComplexModelWithNamespace):
    parentItem = NotBlankUnicode
    children = Array(SelfReference)
    attributes = Array(RefAttribute)
    fields = RefItemField

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит информацию о записи справочника'


class getRefItemsListEntityResponse(ComplexModelWithNamespace):
    totalItems = NotBlankUnicode
    items = RefItem.customize(
        max_occurs='unbounded', min_occurs=0
    )
    version = BlankUnicode
    error = Error

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Ответ содержит информацию о содержимом справочника'
# endregion


class ErrorDetailData(ComplexModelWithNamespace):
    errorCode = NotBlankUnicode
    errorMessage = NotBlankUnicode


class ErrorData(ComplexModelWithNamespace):
    errorDetail = ErrorDetailData


class UpdateBookingDetailsRequest(ComplexModelWithNamespace):
    bookId = NotBlankUnicode
    esiaId = BlankUnicode
    timeSlot = SlotData
    status = NotBlankUnicode

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Схема запроса для сервиса updateBookingDetails'


class UpdateBookingDetailsEntityResponse(ComplexModelWithNamespace):
    bookId = NotBlankUnicode
    esiaId = NotBlankUnicode
    error = ErrorData

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Схема ответа для сервиса updateBookingDetails'


class StatusData(ComplexModelWithNamespace):
    statusCode = NotBlankUnicode
    statusMessage = NotBlankUnicode


class CancelBookingEntityResponse(ComplexModelWithNamespace):
    bookId = NotBlankUnicode
    esiaId = BlankUnicode
    status = NotBlankUnicode
    error = ErrorData

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Схема ответа на отмену заявки'


class CancelBookingRequest(ComplexModelWithNamespace):
    bookId = NotBlankUnicode
    esiaId = BlankUnicode

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Схема запроса на отмену заявки'


# region bookResponse
class BookEntityResponse(ComplexModelWithNamespace):
    bookId = NotBlankUnicode
    esiaId = NotBlankUnicode
    status = StatusData
    timeSlot = SlotData
    error = Error

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Ответ содержит информацию'
# endregion


# region getBookingStatusResponse
class GetBookingStatusResponse(ComplexModelWithNamespace):
    bookId = NotBlankUnicode
    esiaId = NotBlankUnicode
    status = NotBlankUnicode
    timeSlot = SlotData
    error = Error

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Ответ содержит информацию'
# endregion


class GetBookingStatusRequest(ComplexModelWithNamespace):
    bookId = NotBlankUnicode
    esiaId = NotBlankUnicode
    status = NotBlankUnicode

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Схема запроса статуса бранорования'


# region getRefItemsListResponse
class Items(ComplexModelWithNamespace):
    itemName = NotBlankUnicode
    title = NotBlankUnicode

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Контейнер, содержит информацию'


class getRefItemsListResponse(ComplexModelWithNamespace):
    totalItems = NotBlankUnicode
    items = Items.customize(
        max_occurs='unbounded', min_occurs=0
    )

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Ответ содержит информацию'
# endregion


class Attribute(ComplexModelWithNamespace):
    name = NotBlankUnicode
    value = NotBlankUnicode


# Типы заявителя
USER_TYPE_ANONYMOUS = 'ANONYMOUS'
USER_TYPE_BASIC = 'BASIC'
USER_TYPE_SIMPLE = 'SIMPLE'
USER_TYPE_QUALIFIED = 'QUALIFIED'
USER_TYPES = (USER_TYPE_ANONYMOUS, USER_TYPE_BASIC, USER_TYPE_SIMPLE,
              USER_TYPE_QUALIFIED)


class BookRequest(BaseEntityRequest):
    bookId = NotBlankUnicode
    slotId = NotBlankUnicode
    organizationId = Array(NotBlankUnicode)
    userType = Enum(*USER_TYPES, type_name='userType')
    esiaId = BlankUnicode
    serviceId = Array(NotBlankUnicode)
    declarantType = BlankUnicode
    lastName = BlankUnicode
    firstName = BlankUnicode
    middleName = BlankUnicode
    email = BlankUnicode
    mobilePhone = BlankUnicode
    userSnils = BlankUnicode
    userLogin = BlankUnicode
    userDoc = DocumentType
    caseNumber = BlankUnicode
    ChildSurname = BlankUnicode
    ChildName = BlankUnicode
    ChildMiddlename = BlankUnicode
    ChildBirthDate = Date
    ChildDoc = DocumentType
    reasonId = BlankUnicode
    areaId = Array(NotBlankUnicode)
    preliminaryReservation = Boolean
    preliminaryReservationPeriod = Integer
    attributes = Array(Attribute)

    class Annotations(ComplexModelWithNamespace.Annotations):
        doc = 'Описание схемы запроса резервирования заявки'
