# coding:utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from spyne.decorator import rpc

from . import entities, proxy


@rpc(
    entities.NotBlankUnicode,
    entities.NotBlankUnicode,
    entities.Predicate,
    entities.BlankUnicode,
    _returns=entities.getSlotsEntityResponse,
    _out_message_name=b'getSlotsResponse',
)
def getSlotsRequest(self, organizationId, userType, filter, attributes):
    """
    Функция обработки запроса getSlotsRequest
    Метод getSlots - Запросить свободные слоты времени.
    """

    request = entities.getSlotsEntityRequest(
        organizationId=organizationId,
        userType=userType,
        filter=filter,
        attributes=attributes
    )

    return proxy.GetSlotsProxy(
        self, entities.getSlotsEntityResponse, request
    ).process()


@rpc(
    entities.BaseEntityRequest,
    _returns=entities.getRefsListEntityResponse,
    _out_message_name=b'getRefsListResponse',
)
def getRefsListRequest(self, BaseEntityRequest):
    """
    Функция обработки запроса getRefsListRequest
    Метод getRefsList - Метод позволяет ЕПГУ получать информацию о списке
    справочников, имеющихся в системе. Используется для первоначального
    наполнения базы справочной информации ЕПГУ и отображения на этапе
    конфигурирования услуги.
    """
    return proxy.GetRefsListProxy(
        self, entities.getRefsListEntityResponse, BaseEntityRequest
    ).process()


@rpc(
    entities.NotBlankUnicode.customize(max_occurs='unbounded', min_occurs=0),
    _returns=entities.getRefAttributesListEntityResponse,
    _out_message_name=b'getRefAttributesListResponse',
)
def getRefAttributesListRequest(self, refNames):
    """
    Функция обработки запроса getRefAttributesListRequest
    Метод GetRefAttributesList позволяет получать информацию об атрибутах
    конкретного справочника. Используется для первоначального наполнения базы
    справочной информации ЕПГУ и отображения на этапе конфигурирования услуги.
    В рамках услуги "Запись на прием к специалисту" требуется получение
    атрибутов справочника "Учреждение" и "Причина записи на прием" и
    "Тип документа, удостоверяющего личность".
    """

    request = entities.getRefAttributesListEntityRequest(
        refNames=refNames
    )

    return proxy.GetRefAttributesListProxy(
        self, entities.getRefAttributesListEntityResponse, request
    ).process()


@rpc(
    entities.NotBlankUnicode,
    entities.BlankUnicode,
    entities.NotBlankUnicode,
    entities.BlankUnicode.customize(max_occurs='unbounded', min_occurs=0),
    entities.Predicate,
    entities.BlankUnicode.customize(max_occurs='unbounded', min_occurs=0),
    entities.NotBlankUnicode,
    entities.NotBlankUnicode,
    entities.BlankUnicode,
    _returns=entities.getRefItemsListEntityResponse,
    _out_message_name=b'getRefItemsListResponse',
)
def getRefItemsListRequest(
        self, refName, parentRefItemValue, treeFiltering, selectAttributes,
        filter, orderBy, pageNum, pageSize, version,
):
    """
    Функция обработки запроса getRefItemsListRequest
    Метод позволяет получать информацию о данных справочника.
    Используется для первоначального наполнения базы справочной
    информации ЕПГУ, а также для последующей синхронизации.
    """

    request = entities.getRefItemsListEntityRequest(
        refName=refName,
        parentRefItemValue=parentRefItemValue,
        treeFiltering=treeFiltering,
        selectAttributes=selectAttributes,
        filter=filter,
        orderBy=orderBy,
        pageNum=pageNum,
        pageSize=pageSize,
        version=version
    )
    return proxy.GetRefItemsListProxy(
        self, entities.getRefItemsListEntityResponse, request
    ).process()


@rpc(
    entities.NotBlankUnicode,
    entities.BlankUnicode,
    entities.SlotData,
    entities.NotBlankUnicode,
    _returns=entities.UpdateBookingDetailsEntityResponse,
    _out_message_name=b'UpdateBookingDetailsResponse',
)
def updateBookingDetailsRequest(self, bookId, esiaId, timeSlot, status):
    """
    Переносит прием на другой слот.
    """

    request = entities.UpdateBookingDetailsRequest(
        bookId=bookId,
        esiaId=esiaId,
        timeSlot=timeSlot,
        status=status
    )

    return proxy.UpdateBookingDetailsProxy(
        self, entities.UpdateBookingDetailsEntityResponse, request
    ).process()


@rpc(
    entities.NotBlankUnicode,
    entities.BlankUnicode,
    _returns=entities.CancelBookingEntityResponse,
    _out_message_name=b'CancelBookingResponse'
)
def cancelBookingRequest(self, bookId, esiaId):
    """
    Обработка запроса на отмену бронирования записи к специалисту.
    """
    request = entities.CancelBookingRequest(
        bookId=bookId,
        esiaId=esiaId,
    )

    return proxy.CancelBookingProxy(
        self, entities.CancelBookingEntityResponse, request
    ).process()


@rpc(
    entities.NotBlankUnicode,
    entities.NotBlankUnicode,
    entities.NotBlankUnicode.customize(max_occurs='unbounded', min_occurs=0),
    entities.Enum(*entities.USER_TYPES, type_name='userType'),
    entities.BlankUnicode,
    entities.BlankUnicode,
    entities.Array(entities.NotBlankUnicode),
    entities.BlankUnicode,
    entities.BlankUnicode,
    entities.BlankUnicode,
    entities.BlankUnicode,
    entities.BlankUnicode,
    entities.BlankUnicode,
    entities.BlankUnicode,
    entities.DocumentType,
    entities.BlankUnicode,
    entities.BlankUnicode,
    entities.BlankUnicode,
    entities.BlankUnicode,
    entities.Date,
    entities.DocumentType,
    entities.BlankUnicode,
    entities.NotBlankUnicode.customize(max_occurs='unbounded', min_occurs=0),
    entities.Boolean,
    entities.Integer,
    entities.Array(entities.Attribute),
    _returns=entities.BookEntityResponse,
    _out_message_name=b'BookResponse',
)
def bookRequest(
        self, bookId, slotId, organizationId, userType, declarantType, esiaId,
        serviceId, lastName, firstName, middleName, email, mobilePhone,
        userSnils, userLogin, userDoc, caseNumber, ChildSurname, ChildName,
        ChildMiddlename, ChildBirthDate, ChildDoc, reasonId, areaId, 
        preliminaryReservation, preliminaryReservationPeriod, attributes
        
):
    """
    Обработка запрос на бронирование на запись к специалисту.
    """

    request = entities.BookRequest(
        bookId=bookId,
        slotId=slotId,
        organizationId=organizationId,
        userType=userType,
        declarantType=declarantType,
        esiaId=esiaId,
        serviceId=serviceId,
        lastName=lastName,
        firstName=firstName,
        middleName=middleName,
        email=email,
        mobilePhone=mobilePhone,
        userSnils=userSnils,
        userLogin=userLogin,
        userDoc=userDoc,
        caseNumber=caseNumber,
        ChildSurname=ChildSurname,
        ChildName=ChildName,
        ChildMiddlename=ChildMiddlename,
        ChildBirthDate=ChildBirthDate,
        ChildDoc=ChildDoc,
        reasonId=reasonId,
        areaId=areaId,
        preliminaryReservation=preliminaryReservation,
        preliminaryReservationPeriod=preliminaryReservationPeriod,
        attributes=attributes,
    )
    
    return proxy.BookProxy(self, entities.BookEntityResponse, request).process()


@rpc(
    entities.NotBlankUnicode,
    entities.NotBlankUnicode,
    entities.NotBlankUnicode,
    _returns=entities.GetBookingStatusResponse,
    _out_message_name=b'GetBookingResponse',
)
def getBookingStatusRequest(self, bookId, esiaId, status):
    """
    Метод book начинает отправляется в систему в момент выбора необходимого
    слота времени и его бронирования на портале гос.услуг
    """

    request = entities.GetBookingStatusRequest(
        bookId=bookId,
        esiaId=esiaId,
        status=status,
    )

    return proxy.GetBookingStatusProxy(
        self, entities.GetBookingStatusResponse, request
    ).process()
