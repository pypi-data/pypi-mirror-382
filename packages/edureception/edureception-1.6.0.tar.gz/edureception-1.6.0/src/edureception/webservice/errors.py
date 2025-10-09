# coding=utf-8
class EdureceptionServiceError(Exception):
    """
    Исключение для @edureception.webservice.ServerProxy
    Выбрасывается в методе ServiceProxy.do_process
    Когда выбрасывается - ServiceProxy возвращает ответ со статусом ошибки
    """
    pass


class EdureceptionTypeError(Exception):
    """
    Исключение для @edureception.webservice.helper.RefsListEnum
    Выбрасывается в методе _get_fields_model
    Из-за того что тип поля не определен в RefsListEnum.type_fields
    """
    pass
