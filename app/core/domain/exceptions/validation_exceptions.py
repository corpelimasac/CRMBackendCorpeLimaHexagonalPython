"""
Excepciones de validación del dominio
"""


class ValidationException(Exception):
    """
    Excepción base para todas las excepciones de validación
    """
    pass


class InvalidEmailFormatError(ValidationException):
    """
    Excepción lanzada cuando el formato del email es inválido
    """
    pass


class InvalidUserDataError(ValidationException):
    """
    Excepción lanzada cuando los datos del usuario son inválidos
    """
    pass


class InvalidProductDataError(ValidationException):
    """
    Excepción lanzada cuando los datos del producto son inválidos
    """
    pass


class InvalidOrderDataError(ValidationException):
    """
    Excepción lanzada cuando los datos de la orden son inválidos
    """
    pass


class InvalidMoneyAmountError(ValidationException):
    """
    Excepción lanzada cuando el monto monetario es inválido
    """
    pass


class InvalidCurrencyError(ValidationException):
    """
    Excepción lanzada cuando la moneda es inválida
    """
    pass


class RequiredFieldError(ValidationException):
    """
    Excepción lanzada cuando un campo requerido está vacío
    """
    def __init__(self, field_name: str):
        self.field_name = field_name
        super().__init__(f"El campo '{field_name}' es requerido")


class InvalidFieldLengthError(ValidationException):
    """
    Excepción lanzada cuando la longitud de un campo es inválida
    """
    def __init__(self, field_name: str, min_length: int = None, max_length: int = None):
        self.field_name = field_name
        self.min_length = min_length
        self.max_length = max_length
        
        if min_length and max_length:
            message = f"El campo '{field_name}' debe tener entre {min_length} y {max_length} caracteres"
        elif min_length:
            message = f"El campo '{field_name}' debe tener al menos {min_length} caracteres"
        elif max_length:
            message = f"El campo '{field_name}' debe tener máximo {max_length} caracteres"
        else:
            message = f"El campo '{field_name}' tiene una longitud inválida"
        
        super().__init__(message)


class InvalidFieldValueError(ValidationException):
    """
    Excepción lanzada cuando el valor de un campo es inválido
    """
    def __init__(self, field_name: str, value: str, reason: str = None):
        self.field_name = field_name
        self.value = value
        self.reason = reason
        
        message = f"El valor '{value}' del campo '{field_name}' es inválido"
        if reason:
            message += f": {reason}"
        
        super().__init__(message)


class InvalidNumericValueError(ValidationException):
    """
    Excepción lanzada cuando un valor numérico es inválido
    """
    def __init__(self, field_name: str, value: float, min_value: float = None, max_value: float = None):
        self.field_name = field_name
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        
        if min_value is not None and max_value is not None:
            message = f"El campo '{field_name}' debe estar entre {min_value} y {max_value}, valor actual: {value}"
        elif min_value is not None:
            message = f"El campo '{field_name}' debe ser mayor o igual a {min_value}, valor actual: {value}"
        elif max_value is not None:
            message = f"El campo '{field_name}' debe ser menor o igual a {max_value}, valor actual: {value}"
        else:
            message = f"El valor {value} del campo '{field_name}' es inválido"
        
        super().__init__(message) 