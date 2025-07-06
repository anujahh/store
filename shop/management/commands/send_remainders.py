# shop/management/commands/send_reminders.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from shop.models import SavedDate

class Command(BaseCommand):
    help = 'Sends reminders for saved dates that are 5 days away.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        reminder_date = today + timedelta(days=5)
        
        # Find dates that match the reminder date and haven't had a reminder sent
        dates_to_remind = SavedDate.objects.filter(
            event_date=reminder_date, 
            reminder_sent=False
        )
        
        if not dates_to_remind.exists():
            self.stdout.write(self.style.SUCCESS('No reminders to send today.'))
            return

        for saved_date in dates_to_remind:
            user = saved_date.user
            subject = f"Reminder: Your event '{saved_date.event_name}' is soon!"
            message = f"Hi {user.username},\n\nThis is a reminder that your event '{saved_date.event_name}' is scheduled for {saved_date.event_date}.\n\nThat's just 5 days away!\n\nBest,\nThe Nike Store Team"
            
            try:
                send_mail(
                    subject,
                    message,
                    'noreply@nikestore.com', # From email
                    [user.email], # To email
                    fail_silently=False,
                )
                # Mark as sent to avoid duplicate emails
                saved_date.reminder_sent = True
                saved_date.save()
                self.stdout.write(self.style.SUCCESS(f"Successfully sent reminder to {user.email} for '{saved_date.event_name}'"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to send email to {user.email}: {e}"))