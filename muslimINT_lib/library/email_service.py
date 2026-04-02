from django.conf import settings
from sib_api_v3_sdk import Configuration, ApiClient, TransactionalEmailsApi
from sib_api_v3_sdk.rest import ApiException
from sib_api_v3_sdk.models import SendSmtpEmail


def send_brevo_email(to_email, subject, html_content, text_content=None):
    if not to_email:
        return False

    configuration = Configuration()
    configuration.api_key["api-key"] = settings.BREVO_API_KEY

    api_instance = TransactionalEmailsApi(ApiClient(configuration))

    email = SendSmtpEmail(
        to=[{"email": to_email}],
        subject=subject,
        html_content=html_content,
        sender={
            "email": settings.DEFAULT_FROM_EMAIL,
            "name": getattr(settings, "APP_NAME", "Maktaba'Int"),
        },
    )

    if text_content:
        email.text_content = text_content

    try:
        api_instance.send_transac_email(email)
        return True
    except ApiException as e:
        print(f"Erreur Brevo : {e}")
        return False