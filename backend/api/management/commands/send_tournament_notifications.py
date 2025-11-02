from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from api.models import Tournament, TournamentRegistration, Profile
import os
from twilio.rest import Client
from api.views import send_whatsapp_message

class Command(BaseCommand):
    help = 'Send WhatsApp notifications for tournaments starting in 3 days'

    def handle(self, *args, **options):
        # Get tournaments starting in exactly 3 days
        three_days_from_now = timezone.now().date() + timedelta(days=3)
        upcoming_tournaments = Tournament.objects.filter(
            start_date=three_days_from_now,
            status='upcoming',
            notification_sent=False
        )

        if not upcoming_tournaments.exists():
            self.stdout.write('No tournaments starting in 3 days.')
            return

        # Initialize Twilio client
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        whatsapp_number = os.environ.get('TWILIO_WHATSAPP_NUMBER')

        if not all([account_sid, auth_token, whatsapp_number]):
            self.stderr.write('Twilio credentials not configured in environment variables.')
            return

        client = Client(account_sid, auth_token)

        for tournament in upcoming_tournaments:
            self.stdout.write(f'Processing tournament: {tournament.name}')

            # Get all registered participants
            registrations = TournamentRegistration.objects.filter(tournament=tournament)
            participants = [reg.user for reg in registrations]

            # Also include coaches and volunteers who might be interested
            coaches_and_volunteers = Profile.objects.filter(
                user_type__in=['coach', 'volunteer']
            ).select_related('user')

            all_recipients = set(participants + [cv.user for cv in coaches_and_volunteers])

            messages_sent = 0
            for user in all_recipients:
                if user.profile.phone:
                    try:
                        # Use the utility function from views.py
                        success = send_whatsapp_message(
                            to_number=f"+91{user.profile.phone}",  # Assuming Indian numbers, adjust country code as needed
                            message=f"🏆 Tournament Alert! '{tournament.name}' is starting on {tournament.start_date.strftime('%B %d, %Y')} at {tournament.location}. Don't miss out!"
                        )
                        if success:
                            messages_sent += 1
                            self.stdout.write(f'Sent notification to {user.get_full_name()} ({user.profile.phone})')
                        else:
                            self.stderr.write(f'Failed to send to {user.get_full_name()}: Twilio not configured or error')
                    except Exception as e:
                        self.stderr.write(f'Failed to send to {user.get_full_name()}: {str(e)}')

            # Mark notification as sent
            tournament.notification_sent = True
            tournament.save()

            self.stdout.write(f'Sent {messages_sent} WhatsApp notifications for {tournament.name}')

        self.stdout.write('Tournament notification process completed.')
