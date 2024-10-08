import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings

from simple_history.models import HistoricalRecords


class RequestLog(models.Model):
    class Meta:
        db_table = 'activity_log'
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.CharField(max_length=45)
    user_agent = models.TextField()
    path = models.CharField(max_length=200)
    query_string = models.TextField()
    body = models.TextField()
    method = models.CharField(max_length=10)
    response_status = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)


class DefaultAuthUserExtend(AbstractUser):
    class Meta:
        db_table = 'auth_user_extend'
        verbose_name = 'User Master'
        verbose_name_plural = 'User Masters'

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    contact_no = models.CharField(max_length=10, null=True, db_index=True, default='', blank=True,
                                  validators=[RegexValidator(regex=r'^[0-9- ]+$', message="Invalid phone number")])
    token_version = models.IntegerField(default=1)

    history = HistoricalRecords(table_name="history_auth_user_extend")

    def __str__(self):
        return f"{self.email} {self.first_name}"


class AdminMenuMaster(models.Model):
    class Meta:
        db_table = "admin_menu_master"
        verbose_name = "Admin Menu"
        verbose_name_plural = "Admin Menus"

    id = models.SmallAutoField(primary_key=True, db_column='id', db_index=True, editable=False, unique=True,
                               blank=False, null=False, verbose_name='ID')
    parent_id = models.ForeignKey('self', null=True, blank=True, related_name='submenus', db_column='parent_id',
                                  on_delete=models.CASCADE)
    menu_name = models.CharField(max_length=30, null=False, blank=False, unique=True,
                                 validators=[RegexValidator(regex=r'^[a-zA-Z0-9()\s]+$', message="Invalid characters")])
    menu_icon = models.CharField(max_length=20, null=True, blank=True, default='list',
                                 validators=[RegexValidator(regex=r'^[a-z0-9-]+$', message="Invalid characters")])
    menu_route = models.CharField(max_length=30, null=True, blank=True,
                                  validators=[RegexValidator(regex=r'^[a-zA-Z0-9\s-]+$', message="Invalid characters")])
    menu_access = models.CharField(max_length=30, null=True, blank=True,
                                   validators=[RegexValidator(regex=r'^[a-zA-Z0-9\s-]+$', message="Invalid characters")])
    menu_order = models.SmallIntegerField(null=True, blank=True,
                                          validators=[RegexValidator(regex=r'^[0-9]+$', message="Invalid characters")])

    status = models.BooleanField(default=True, verbose_name='Status')
    deleted = models.BooleanField(default=False, verbose_name='Is Deleted')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Deleted At')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    def __str__(self):
        return f"{self.menu_name} ({self.menu_route})"


class PermissionMaster(models.Model):
    class Meta:
        unique_together = ('menu', 'action')
        db_table = "permission_master"
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"

    ACTION_CHOICES = (
        ('add', 'add'),
        ('edit', 'edit'),
        ('view', 'view'),
        ('delete', 'delete'),
    )
    id = models.AutoField(primary_key=True, db_column='id', db_index=True, editable=False, unique=True,
                          blank=False, null=False, verbose_name='ID')

    menu = models.ForeignKey(AdminMenuMaster, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    is_virtual = models.BooleanField(default=False)

    status = models.BooleanField(default=True, verbose_name='Status')
    deleted = models.BooleanField(default=False, verbose_name='Is Deleted')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Deleted At')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    def __str__(self):
        return f"{self.menu.menu_route}_{self.action}"


class CustomPermissions(models.Model):
    class Meta:
        db_table = "custom_permissions"
        verbose_name = "Custom Permission"
        verbose_name_plural = "Custom Permissions"
        unique_together = ('user', 'permission_name')

    id = models.AutoField(primary_key=True, db_column='id', db_index=True, editable=False, unique=True,
                             blank=False, null=False, verbose_name='ID')

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    # permission_name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    permission_name = models.ForeignKey(PermissionMaster, on_delete=models.CASCADE)

    status = models.BooleanField(default=True, verbose_name='Status')
    deleted = models.BooleanField(default=False, verbose_name='Is Deleted')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Deleted At')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    def __str__(self):
        return str(self.permission_name)


class GroupCustomPermissions(models.Model):
    class Meta:
        db_table = "custom_group_permissions"
        verbose_name = "Group Custom Permission"
        verbose_name_plural = "Group Custom Permissions"
        # unique_together = ('group', 'permission_name')

    id = models.AutoField(primary_key=True, db_column='id', db_index=True, editable=False, unique=True,
                          blank=False, null=False, verbose_name='ID')

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    permission_names = models.ManyToManyField(PermissionMaster)

    status = models.BooleanField(default=True, verbose_name='Status')
    deleted = models.BooleanField(default=False, verbose_name='Is Deleted')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Deleted At')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    def __str__(self):
        return f"{self.group} {str(self.permission_names)}"


