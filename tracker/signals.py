# tracker/signals.py
import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User # Assuming standard User model

from .models import LLC, Property, Tenant, Payment, PropertyFinancialHistory
from .middleware import get_current_user # Import the function to get the user

# Get an instance of a logger (we'll configure this in settings.py)
action_logger = logging.getLogger('tracker.actions')

# List of models we want to log actions for
LOGGED_MODELS = [LLC, Property, Tenant, Payment]

@receiver(post_save)
def log_post_save(sender, instance, created, **kwargs):
    """
    Logs when an instance of a tracked model is saved (created or updated).
    """
    if sender in LOGGED_MODELS:
        user = get_current_user()
        user_str = str(user) if user and user.is_authenticated else "System/Unknown"

        action = "Added" if created else "Changed"

        # Log the action
        action_logger.info(
            f"User '{user_str}' {action} {sender.__name__}: '{str(instance)}' (ID: {instance.pk})"
        )
        # You could add more details here if needed, like changed fields (more complex)

@receiver(post_delete)
def log_post_delete(sender, instance, **kwargs):
    """
    Logs when an instance of a tracked model is deleted.
    """
    if sender in LOGGED_MODELS:
        user = get_current_user()
        user_str = str(user) if user and user.is_authenticated else "System/Unknown"

        # Log the action
        action_logger.info(
            f"User '{user_str}' Deleted {sender.__name__}: '{str(instance)}' (ID: {instance.pk})"
        )

@receiver(pre_save, sender=Property)
def track_property_financial_changes(sender, instance, **kwargs):
    """
    Before a Property is saved, check if financial fields have changed
    and log the change to the history model.
    """
    if instance.pk is None: # This is a new object, not an update.
        return

    try:
        old_instance = Property.objects.get(pk=instance.pk)
    except Property.DoesNotExist:
        return # Should not happen if pk exists, but it's safe to check.

    user = get_current_user()
    tracked_fields = ['rent_amount', 'home_payment', 'lot_payment']
    history_records_to_create = []

    for field in tracked_fields:
        old_value = getattr(old_instance, field)
        new_value = getattr(instance, field)

        if old_value != new_value:
            history_records_to_create.append(
                PropertyFinancialHistory(property=instance, field_name=field, old_value=old_value, new_value=new_value, changed_by=user)
            )

    if history_records_to_create:
        PropertyFinancialHistory.objects.bulk_create(history_records_to_create)