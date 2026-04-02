from django.conf import settings
from .email_service import send_brevo_email


def send_due_soon_email(loan):
    borrower = loan.borrower
    book = loan.book
    app_name = getattr(settings, "APP_NAME", "MaktabaInt - Asso MuslimINT")

    if not borrower.email:
        return False

    due_str = loan.due_date.strftime("%d/%m/%Y")
    borrower_name = borrower.first_name or borrower.username

    subject = f"Rappel - retour du livre « {book.title} »"

    html_content = f"""
    <h2>Rappel de retour</h2>
    <p>Bonjour {borrower_name},</p>
    <p>Le livre <strong>{book.title}</strong> doit être rendu avant le <strong>{due_str}</strong>.</p>
    <p>Merci de penser à le retourner à temps.</p>
    <p>L’équipe {app_name}</p>
    """

    text_content = (
        f"Bonjour {borrower_name},\n\n"
        f"Le livre '{book.title}' doit être rendu avant le {due_str}.\n"
        f"Merci de penser à le retourner à temps.\n\n"
        f"L’équipe {app_name}"
    )

    return send_brevo_email(
        borrower.email,
        subject,
        html_content,
        text_content
    )


def send_overdue_email(loan):
    borrower = loan.borrower
    book = loan.book
    app_name = getattr(settings, "APP_NAME", "MaktabaInt")

    if not borrower.email:
        return False

    due_str = loan.due_date.strftime("%d/%m/%Y")
    borrower_name = borrower.first_name or borrower.username

    subject = f"Retard - livre « {book.title} »"

    html_content = f"""
    <h2>Livre en retard</h2>
    <p>Bonjour {borrower_name},</p>
    <p>Le livre <strong>{book.title}</strong> aurait dû être rendu le <strong>{due_str}</strong>.</p>
    <p>Merci de le retourner dès que possible.</p>
    <p>L’équipe {app_name}</p>
    """

    text_content = (
        f"Bonjour {borrower_name},\n\n"
        f"Le livre '{book.title}' aurait dû être rendu le {due_str}.\n"
        f"Merci de le retourner dès que possible.\n\n"
        f"L’équipe {app_name}"
    )

    return send_brevo_email(
        borrower.email,
        subject,
        html_content,
        text_content
    )