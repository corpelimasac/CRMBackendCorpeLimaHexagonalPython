"""
Excepciones de negocio del dominio
"""


class DomainException(Exception):
    """
    Excepción base para todas las excepciones del dominio
    """
    pass


class UserAlreadyExistsError(DomainException):
    """
    Excepción lanzada cuando se intenta crear un usuario que ya existe
    """
    pass


class UserNotFoundError(DomainException):
    """
    Excepción lanzada cuando no se encuentra un usuario
    """
    pass


class InvalidUserDataError(DomainException):
    """
    Excepción lanzada cuando los datos del usuario son inválidos
    """
    pass


class ProductNotFoundError(DomainException):
    """
    Excepción lanzada cuando no se encuentra un producto
    """
    pass


class ProductAlreadyExistsError(DomainException):
    """
    Excepción lanzada cuando se intenta crear un producto que ya existe
    """
    pass


class OrderNotFoundError(DomainException):
    """
    Excepción lanzada cuando no se encuentra una orden
    """
    pass


class InvalidOrderStateError(DomainException):
    """
    Excepción lanzada cuando se intenta realizar una operación inválida en una orden
    """
    pass


class InsufficientStockError(DomainException):
    """
    Excepción lanzada cuando no hay suficiente stock para procesar una orden
    """
    pass 