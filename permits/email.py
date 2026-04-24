from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_permit_email(permit):
    subject = "Autorizzazione transito / Transitgenehmigung / Transit permit"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [permit.email]

    context = {"permit": permit, "site_url": settings.SITE_URL}

    text_body = render_to_string("emails/permit_invite.txt", context)
    html_body = render_to_string("emails/permit_invite.html", context)

    msg = EmailMultiAlternatives(subject, text_body, from_email, to)
    msg.attach_alternative(html_body, "text/html")
    try:
        msg.send()
    except Exception as e:
        print(f"Error sending email: {e}")  
