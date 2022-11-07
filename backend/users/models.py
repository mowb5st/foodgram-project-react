from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy

ROLE_ADMIN = 'admin'
ROLE_USER = 'user'
ROLES = (
    (ROLE_ADMIN, 'Администратор'),
    (ROLE_USER, 'Пользователь')
)


class User(AbstractUser):
    username = models.CharField(
        'Логин', max_length=150, unique=True)
    password = models.CharField(gettext_lazy('password'), max_length=128)
    email = models.EmailField(
        'Почта', max_length=254, unique=True)
    role = models.CharField(
        'Роль', choices=ROLES, default=ROLE_USER, max_length=15)
    first_name = models.CharField(
        'Имя', max_length=150, blank=False)
    last_name = models.CharField(
        'Фамилия', max_length=150, blank=False)

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN or self.is_staff

    @property
    def is_user(self):
        return self.role == ROLE_USER
