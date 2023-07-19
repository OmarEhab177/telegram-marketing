from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError

def validate_weak_password(value):
    min_length = 4

    if len(value) < min_length:
        raise ValidationError(
            "Password must be at least %(min_length)d characters long.",
            params={'min_length': min_length},
        )

class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if username is None:
            raise TypeError('Users must have a username.')

        user = self.model(username=username)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, password):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, password)
        user.is_superuser = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, db_index=True)
    password = models.CharField(max_length=128, validators=[validate_weak_password])
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.username


class TelegramAccount(User):
    phone_number = models.CharField(max_length=20)
    api_id = models.CharField(max_length=255)
    api_hash = models.CharField(max_length=255)
    last_login_date = models.DateTimeField(null=True, blank=True)
    phone_code_hash = models.CharField(max_length=255, null=True, blank=True)


class Member(models.Model):
    member_id = models.BigIntegerField()
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    access_hash = models.CharField(max_length=255)

class Channel(models.Model):
    channel_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    is_channel = models.BooleanField(default=False)
    is_group = models.BooleanField(default=False)
    telegram_account = models.ForeignKey(TelegramAccount, on_delete=models.CASCADE, related_name='channels')
    members = models.ManyToManyField(Member, through='ChannelMembers', related_name='channels')


class ChannelMembers(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    # Add any additional fields related to the relationship here

    class Meta:
        unique_together = ('channel', 'member')
