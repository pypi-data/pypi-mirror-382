"""
Biblioteca compartilhada para acesso aos models de autenticação
"""
from .models import (
    SharedOrganization,
    SharedUser,
    SharedMember,
)
from .exceptions import (
    OrganizationNotFoundError,
    UserNotFoundError,
)

__version__ = '1.0.0'
__all__ = [
    'SharedOrganization',
    'SharedUser',
    'SharedMember',
    'OrganizationNotFoundError',
    'UserNotFoundError',
]
