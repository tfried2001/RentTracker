# tracker/management/commands/reset_llc_filing_status.py
from django.core.management.base import BaseCommand
from tracker.models import LLC
import datetime

class Command(BaseCommand):
    help = 'Resets the filing_current status for all LLCs to False. Intended to be run at the start of a new year.'

    def handle(self, *args, **kwargs):
        current_year = datetime.date.today().year
        self.stdout.write(
            f"Starting reset of LLC filing status for the year {current_year}..."
        )

        updated_count = LLC.objects.update(filing_current=False)

        self.stdout.write(self.style.SUCCESS(
            f"Successfully reset 'filing_current' to False for {updated_count} LLC(s)."
        ))