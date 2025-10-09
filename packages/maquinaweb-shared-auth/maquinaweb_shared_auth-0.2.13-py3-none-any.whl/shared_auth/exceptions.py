"""
Exceções customizadas
"""
class SharedAuthError(Exception):
    """Erro base da biblioteca"""
    pass


class OrganizationNotFoundError(SharedAuthError):
    """Organização não encontrada"""
    pass


class UserNotFoundError(SharedAuthError):
    """Usuário não encontrado"""
    pass


class DatabaseConnectionError(SharedAuthError):
    """Erro de conexão com o banco de dados"""
    pass