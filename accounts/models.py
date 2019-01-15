from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    userid = models.CharField(max_length=200, null=True, blank=True)
    pin = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.__str__()


class MailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hash_code = models.CharField(max_length=400, blank=True, null=True)
    mail_id = models.EmailField(null=True, blank=True)
    time_limit = models.DateField(default=timezone.now().date())
    mail_type = models.IntegerField(default=0)

    def __str__(self):
        return self.user.__str__()
