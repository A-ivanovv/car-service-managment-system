from django.core.management.base import BaseCommand
from dashboard.models import Sklad


class Command(BaseCommand):
    help = 'Clear all records from Sklad table'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all Sklad records',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL records from the Sklad table!\n'
                    'Use --confirm flag to proceed.'
                )
            )
            return

        # Get count before deletion
        count = Sklad.objects.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('Sklad table is already empty.')
            )
            return

        # Delete all records
        Sklad.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {count} records from Sklad table.'
            )
        )
