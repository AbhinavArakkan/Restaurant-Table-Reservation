from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    # Add more fields as needed for the user profile

    def __str__(self):
        return self.user.username

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seats = models.CharField(max_length=1)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    special_request = models.TextField(blank=True, null=True)
    menu = models.TextField(blank=True)

