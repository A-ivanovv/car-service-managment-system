from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DaysOff


@receiver(post_save, sender=DaysOff)
def update_employee_leave_usage(sender, instance, created, **kwargs):
    """Update employee leave usage when days off are saved"""
    if instance.is_approved and instance.day_off_type == 'vacation':
        instance.employee.update_leave_usage()


@receiver(post_delete, sender=DaysOff)
def update_employee_leave_usage_on_delete(sender, instance, **kwargs):
    """Update employee leave usage when days off are deleted"""
    if instance.is_approved and instance.day_off_type == 'vacation':
        instance.employee.update_leave_usage()
