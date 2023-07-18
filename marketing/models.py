from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class TelegramAccount(AbstractBaseUser):
    username = models.CharField(max_length=255)
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
