from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from . models import Menu, Reservation,UserProfile
from . tasks import send_confirmation_email_task


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profile_photo = forms.ImageField(required=False)
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'profile_photo', 'phone_number']

class ReservationForm(forms.ModelForm):

    SEATS_CHOICES = [
        (2, '2'),
        (4, '4'),
        (6, '6'),
        (8, '8'),
    ]

    menu = forms.ModelChoiceField(queryset=Menu.objects.all(), empty_label=None)
    seats = forms.TypedChoiceField(choices=SEATS_CHOICES, coerce=int)
    reservation_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))
    reservation_time = forms.CharField(max_length=10,required=True) 
  
    class Meta:
        model = Reservation
        fields = ['seats', 'reservation_date', 'reservation_time', 'special_request','menu']

    def send_email(self):
        user = self.instance.user
        reservation = self.instance
        qr_code_url = reservation.qr_code.url if reservation.qr_code else None


        send_confirmation_email_task.delay(
            username=user.username,
            email=user.email,
            seats=self.cleaned_data['seats'],
            reservation_date=self.cleaned_data['reservation_date'],
            reservation_time=self.cleaned_data['reservation_time'],
            qr_code_url=qr_code_url,
        )

class ProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_photo']
        
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

