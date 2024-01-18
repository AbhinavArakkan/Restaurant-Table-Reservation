from django.contrib.auth.models import User
from django.db import models
from django.core.files.base import ContentFile
import pyqrcode
from io import BytesIO
from django.utils import timezone



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile_photos/', default='profile_photos/profile-picture.png')
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    # Add more fields as needed for the user profile

    def __str__(self):
        return self.user.username
User._meta.get_field('email')._unique = True

class Menu(models.Model):
    food_name = models.CharField(max_length=255)

    def __str__(self):
        return self.food_name


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seats = models.CharField(max_length=1)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    special_request = models.TextField(blank=True, null=True)
    menu = models.TextField(blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Generate QR code content
        current_time = timezone.now().strftime('%H:%M:%S')
        qr_content = f"Username: {self.user.username}, Seats: {self.seats}, Date: {self.reservation_date}, Time: {self.reservation_time}, Current Time: {current_time}"

        # Create QR code
        qr = pyqrcode.create(qr_content)

        # Save QR code to BytesIO
        stream = BytesIO()
        qr.png(stream, scale=2)
        stream.seek(0)

        # Save QR code to ImageField
        self.qr_code.save(f'{self.user.username}_qr.png', ContentFile(stream.read()), save=False)

        super().save(*args, **kwargs)

