from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Parcel(models.Model):
    parcel_id = models.CharField(max_length=200)
    delivery_service = models.CharField(max_length=200)
    date_taken = models.DateTimeField(default=timezone.now())
    student = models.CharField(max_length=200)
    added_by = models.ForeignKey(User, related_name='delivered_by', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('parcel-detail', args=[self.pk])

    def __str__(self):
        return self.parcel_id + "--" + self.delivery_service


class Delivary(models.Model):
    clerk = models.ForeignKey(User, on_delete=models.CASCADE)
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE)

    def __str__(self):
        return self.clerk.username + "--" + self.parcel.__str__()


