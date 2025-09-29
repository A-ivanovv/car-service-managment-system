from django.core.management.base import BaseCommand
from dashboard.models import Car

class Command(BaseCommand):
    help = 'Fix car encoding issues'

    def handle(self, *args, **options):
        self.stdout.write('Fixing car encoding issues...')
        
        # Fix common patterns
        fixes = [
            ('ГЏГЂГђГ'ГЌГ…Гђ', 'ПАРТНЕР'),
            ('ГЃГ…ГђГ‹Г€ГЌГѓГЋ', 'ПЕЖО'),
            ('ГЉГ'ГЂГђГЌГ'Гџ', 'СИТРОЕН'),
            ('ГђГ…ГЌГЋ', 'РЕНО'),
            ('ГЏГ€ГЉГЂГ'ГЋ', 'ПИКАСО'),
        ]
        
        total_fixed = 0
        for garbled, correct in fixes:
            cars = Car.objects.filter(brand_model=garbled)
            count = cars.count()
            if count > 0:
                cars.update(brand_model=correct)
                total_fixed += count
                self.stdout.write(f'Fixed {count} cars: {garbled} → {correct}')
        
        self.stdout.write(f'Total fixed: {total_fixed} cars')
        
        remaining = Car.objects.filter(brand_model__contains='Г').count()
        self.stdout.write(f'Remaining with encoding issues: {remaining}')
