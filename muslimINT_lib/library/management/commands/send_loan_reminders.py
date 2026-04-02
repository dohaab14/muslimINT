from datetime import timedelta

from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from library.models import Loan


class Command(BaseCommand):
    help = "Envoie les emails de rappel et de retard"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        soon_limit = now + timedelta(days=2)

        # 1. Mettre à jour les emprunts en retard
        Loan.objects.filter(
            status='ongoing',
            due_date__lt=now
        ).update(status='overdue')

        # 2. Envoyer les rappels pour les livres à rendre bientôt
        due_soon_loans = Loan.objects.filter(
            status='ongoing',
            due_date__gte=now,
            due_date__lte=soon_limit,
            reminder_sent=False,
        ).select_related('book', 'borrower')

        soon_sent = 0

        for loan in due_soon_loans:
            if loan.borrower.email:
                try:
                    send_mail(
                        subject="Rappel - retour de livre bientôt",
                        message=(
                            f"Bonjour {loan.borrower.first_name or loan.borrower.username},\n\n"
                            f'Le livre "{loan.book.title}" doit être rendu avant le '
                            f'{loan.due_date.strftime("%d/%m/%Y à %H:%M")}.\n\n'
                            f"Merci de penser à le retourner à temps.\n\n"
                            f"L'équipe Maktaba'Int"
                        ),
                        from_email=None,
                        recipient_list=[loan.borrower.email],
                        fail_silently=False,
                    )
                    loan.reminder_sent = True
                    loan.save(update_fields=["reminder_sent"])
                    soon_sent += 1
                except Exception as e:
                    print(f"Erreur rappel pour {loan.borrower.email}: {e}")

        # 3. Envoyer les alertes pour les livres en retard
        overdue_loans = Loan.objects.filter(
            status='overdue',
            overdue_email_sent=False,
        ).select_related('book', 'borrower')

        overdue_sent = 0

        for loan in overdue_loans:
            if loan.borrower.email:
                try:
                    send_mail(
                        subject="Alerte - livre en retard",
                        message=(
                            f"Bonjour {loan.borrower.first_name or loan.borrower.username},\n\n"
                            f'Le livre "{loan.book.title}" est en retard.\n'
                            f'La date limite était le {loan.due_date.strftime("%d/%m/%Y à %H:%M")}.\n\n'
                            f"Merci de le rendre dès que possible.\n\n"
                            f"L'équipe Maktaba'Int"
                        ),
                        from_email=None,
                        recipient_list=[loan.borrower.email],
                        fail_silently=False,
                    )
                    loan.overdue_email_sent = True
                    loan.save(update_fields=["overdue_email_sent"])
                    overdue_sent += 1
                except Exception as e:
                    print(f"Erreur retard pour {loan.borrower.email}: {e}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Emails envoyés : {soon_sent} rappels, {overdue_sent} retards."
            )
        )