from django.core.management.base import BaseCommand
from dashboard.models import Employee


class Command(BaseCommand):
    help = 'Update leave usage for all employees'

    def handle(self, *args, **options):
        employees = Employee.objects.all()
        updated_count = 0
        
        for employee in employees:
            old_usage = employee.current_year_leave_used
            employee.update_leave_usage()
            new_usage = employee.current_year_leave_used
            
            if old_usage != new_usage:
                updated_count += 1
                self.stdout.write(
                    f"Updated {employee.full_name}: {old_usage} -> {new_usage} days"
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} employees')
        )
