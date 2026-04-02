from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from library.models import Loan
from library.loan_notifications import send_due_soon_email, send_overdue_email


class Command(BaseCommand):
    help = "Envoie les rappels email des emprunts"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        today = now.date()
        due_soon_date = today + timedelta(days=2)

        sent_due_soon = 0
        sent_overdue = 0

        # Rappel 2 jours avant
        due_soon_loans = Loan.objects.filter(
            status='ongoing',
            due_date__date=due_soon_date,
            reminder_sent=False,
        ).select_related('borrower', 'book')

        for loan in due_soon_loans:
            if send_due_soon_email(loan):
                loan.reminder_sent = True
                loan.save(update_fields=['reminder_sent'])
                sent_due_soon += 1

        # Mettre à jour les retards
        Loan.objects.filter(status='ongoing', due_date__lt=now).update(status='overdue')

        # Email de retard
        overdue_loans = Loan.objects.filter(
            status='overdue',
            overdue_email_sent=False,
        ).select_related('borrower', 'book')

        for loan in overdue_loans:
            if send_overdue_email(loan):
                loan.overdue_email_sent = True
                loan.save(update_fields=['overdue_email_sent'])
                sent_overdue += 1

        self.stdout.write(self.style.SUCCESS(
            f"Rappels envoyés : {sent_due_soon} | Retards envoyés : {sent_overdue}"
        ))