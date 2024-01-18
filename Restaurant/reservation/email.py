from django.template import Context
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import datetime


def send_confirmation_email(username, email, seats, reservation_date, reservation_time, qr_code_url):

    context = {
        'name': username,
        'email': email,
        'seats': seats,
        'time': datetime.strptime(reservation_time, '%H:%M').strftime('%I:%M %p'),
        'date' : reservation_date,
        'qr_code_url': qr_code_url,
    }

    email_subject = "Your Reservation Confirmation at Queen's Feast"
    email_body = render_to_string('reservation/email_message.txt', context)

    email = EmailMessage(
        email_subject, email_body,
        settings.DEFAULT_FROM_EMAIL, [email],
    )    

    if qr_code_url:
        qr_code_path = qr_code_url[len(settings.MEDIA_URL):] 
        email.attach_file(qr_code_path)

    return email.send(fail_silently=False)


def send_reservation_details_email(username, email, seats, date, time, qr_code):
    context = {
        'name': username,
        'email': email,
        'seats': seats,
        'time': time,
        'date' : date,
        'qr_code_url': qr_code,
    }

    email_subject = "Your Reservation Details at Queen's Feast"
    email_body = render_to_string('reservation/reservation_details.txt', context)

    email = EmailMessage(
        email_subject, email_body,
        settings.DEFAULT_FROM_EMAIL, [email],
    )    

    if qr_code:
        qr_code_path = qr_code[len(settings.MEDIA_URL):] 
        email.attach_file(qr_code_path)

    return email.send(fail_silently=False)