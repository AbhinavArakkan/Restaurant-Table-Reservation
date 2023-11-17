from celery import shared_task   
from celery.utils.log import get_task_logger

from .email import send_confirmation_email

logger = get_task_logger(__name__)


@shared_task(name="send_confirmation_email_task", bind=True)
def send_confirmation_email_task(self, username, email, seats, reservation_date, reservation_time ):
    logger.info("Sent confirmation email")
    return send_confirmation_email(username=username, email=email, seats=seats, reservation_date=reservation_date, reservation_time=reservation_time )
