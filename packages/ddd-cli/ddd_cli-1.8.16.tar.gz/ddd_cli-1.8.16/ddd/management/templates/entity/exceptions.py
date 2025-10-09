# domain/exceptions.py

class [[ entity_name.capitalize() ]]Error(Exception):
    """Excepción base para errores relacionados con el dominio [[ entity_name.capitalize() ]]."""
    pass


class [[ entity_name.capitalize() ]]ValueError([[ entity_name.capitalize() ]]Error):
    """Error de valor en atributos de la entidad [[ entity_name.capitalize() ]]."""
    def __init__(self, detail: str, field: str = "value"):
        self.field = field
        self.detail = detail
        if field == "value":
            super().__init__(f"Value error: {detail}.")
        else:
            super().__init__(f"Field error in '{field}': {detail}.")


class [[ entity_name.capitalize() ]]ValidationError([[ entity_name.capitalize() ]]Error):
    """Errores de validación de datos antes de guardar el modelo."""
    def __init__(self, errors):
        self.errors = errors
        super().__init__("Validation in [[ entity_name.capitalize() ]] failed.")


class [[ entity_name.capitalize() ]]AlreadyExistsError([[ entity_name.capitalize() ]]Error):
    """Cuando se intenta crear una [[ entity_name.capitalize() ]] que ya existe."""
    def __init__(self, detail: str, field: str = "value"):
        self.field = field        
        self.detail = detail
        super().__init__(f"[[ entity_name.capitalize() ]] already exists.")


class [[ entity_name.capitalize() ]]NotFoundError([[ entity_name.capitalize() ]]Error):
    """Cuando se intenta acceder a una [[ entity_name.capitalize() ]] inexistente."""
    def __init__(self, id):
        self.id = id
        super().__init__(f"[[ entity_name.capitalize() ]] with ID {id} not.")


class [[ entity_name.capitalize() ]]OperationNotAllowedError([[ entity_name.capitalize() ]]Error):
    """Cuando se intenta realizar una operación no permitida."""
    def __init__(self, operation_name: str):
        super().__init__(f"Operation '{operation_name}' not allowed in [[ entity_name.capitalize() ]].")        


class [[ entity_name.capitalize() ]]PermissionError([[ entity_name.capitalize() ]]Error):
    """Cuando el usuario no tiene permisos para modificar o acceder."""
    def __init__(self):
        super().__init__("Permission not allowed in [[ entity_name.capitalize() ]].")      
