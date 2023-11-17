from django.template import Context
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings


def send_confirmation_email(username, email, seats, reservation_date, reservation_time ):

    context = {
        'name': username,
        'email': email,
        'seats': seats,
        'time' : reservation_time,
        'date' : reservation_date

    }

    email_subject = "Your Reservation Confirmation at Queen's Feast"
    email_body = render_to_string('reservation/email_message.txt', context)

    email = EmailMessage(
        email_subject, email_body,
        settings.DEFAULT_FROM_EMAIL, [email],
    )    
    return email.send(fail_silently=False)