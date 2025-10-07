"""
Models READ-ONLY para acesso aos dados de autenticação
ATENÇÃO: Estes models NÃO devem ser usados para criar migrations
"""

from django.db import models
from .conf import ORGANIZATION_TABLE, USER_TABLE, MEMBER_TABLE
from .managers import (
    SharedOrganizationManager,
    SharedUserManager,
    SharedMemberManager,
)


class SharedToken(models.Model):
    """
    Model READ-ONLY da tabela authtoken_token
    Usado para validar tokens em outros sistemas
    """

    key = models.CharField(max_length=40, primary_key=True)
    user_id = models.IntegerField()
    created = models.DateTimeField()

    objects = models.Manager()

    class Meta:
        managed = False
        db_table = "authtoken_token"
        app_label = "shared_auth"

    def __str__(self):
        return self.key

    @property
    def user(self):
        """Acessa usuário do token"""
        if not hasattr(self, "_cached_user"):
            self._cached_user = SharedUser.objects.using("auth_db").get_or_fail(
                self.user_id
            )
        return self._cached_user

    def is_valid(self):
        """Verifica se token ainda é válido"""
        # Implementar lógica de expiração se necessário
        return True


class SharedOrganization(models.Model):
    """
    Model READ-ONLY da tabela organization
    Usado para acessar dados de organizações em outros sistemas
    """

    # Campos principais
    name = models.CharField(max_length=255)
    fantasy_name = models.CharField(max_length=255, blank=True, null=True)
    cnpj = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=50, blank=True, null=True)
    cellphone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # Relacionamentos
    main_organization_id = models.IntegerField(null=True, blank=True)
    is_branch = models.BooleanField(default=False)

    # Metadados
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SharedOrganizationManager()

    class Meta:
        managed = False  # CRITICAL: Não gera migrations
        db_table = ORGANIZATION_TABLE
        app_label = "shared_auth"

    def __str__(self):
        return self.fantasy_name or self.name or f"Org #{self.pk}"

    @property
    def main_organization(self):
        """
        Acessa organização principal (lazy loading)

        Usage:
            if org.is_branch:
                main = org.main_organization
        """
        if self.main_organization_id:
            return SharedOrganization.objects.get_or_fail(self.main_organization_id)
        return None

    @property
    def branches(self):
        """
        Retorna filiais desta organização

        Usage:
            branches = org.branches
        """
        return SharedOrganization.objects.filter(main_organization_id=self.pk)

    @property
    def members(self):
        """
        Retorna membros desta organização

        Usage:
            members = org.members
            for member in members:
                print(member.user.email)
        """
        return SharedMember.objects.for_organization(self.pk)

    @property
    def users(self):
        """
        Retorna usuários desta organização

        Usage:
            users = org.users
        """
        return SharedUser.objects.filter(
            id__in=self.members.values_list("user_id", flat=True)
        )

    def is_active(self):
        """Verifica se organização está ativa"""
        return self.deleted_at is None


class SharedUser(models.Model):
    """
    Model READ-ONLY da tabela auth_user
    """

    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField()
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField()
    last_login = models.DateTimeField(null=True, blank=True)

    # Campos customizados
    logged_organization_id = models.IntegerField(null=True, blank=True)
    createdat = models.DateTimeField()
    updatedat = models.DateTimeField()
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SharedUserManager()

    class Meta:
        managed = False
        db_table = USER_TABLE
        app_label = "shared_auth"

    def __str__(self):
        return self.get_full_name() or self.username

    def get_full_name(self):
        """Retorna nome completo"""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def logged_organization(self):
        """
        Acessa organização logada (lazy loading)

        Usage:
            user = SharedUser.objects.get(pk=1)
            org = user.logged_organization
            print(org.name)
        """
        if self.logged_organization_id:
            return SharedOrganization.objects.get_or_fail(self.logged_organization_id)
        return None

    @property
    def organizations(self):
        """
        Retorna todas as organizações do usuário

        Usage:
            orgs = user.organizations
        """
        member_orgs = SharedMember.objects.for_user(self.pk)
        org_ids = member_orgs.values_list("organization_id", flat=True)
        return SharedOrganization.objects.filter(pk__in=org_ids)

    @property
    def memberships(self):
        """
        Retorna memberships do usuário

        Usage:
            memberships = user.memberships
            for m in memberships:
                print(m.organization.name)
        """
        return SharedMember.objects.for_user(self.pk)


class SharedMember(models.Model):
    """
    Model READ-ONLY da tabela organization_member
    Relacionamento entre User e Organization
    """

    user_id = models.IntegerField()
    organization_id = models.IntegerField()
    metadata = models.JSONField(default=dict)

    objects = SharedMemberManager()

    class Meta:
        managed = False
        db_table = MEMBER_TABLE
        app_label = "shared_auth"

    def __str__(self):
        return f"Member: User {self.user_id} - Org {self.organization_id}"

    @property
    def user(self):
        """
        Acessa usuário (lazy loading)

        Usage:
            member = SharedMember.objects.first()
            user = member.user
            print(user.email)
        """
        return SharedUser.objects.get_or_fail(self.user_id)

    @property
    def organization(self):
        """
        Acessa organização (lazy loading)

        Usage:
            member = SharedMember.objects.first()
            org = member.organization
            print(org.name)
        """
        return SharedOrganization.objects.get_or_fail(self.organization_id)
