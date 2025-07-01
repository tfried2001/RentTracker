# tracker/models/tenant.py
from django.db import models

from .property import Property


class Tenant(models.Model):
    """Represents a tenant renting a property."""
    class IdentificationTypeChoices(models.TextChoices):
        DRIVERS_LICENSE = 'DL', "Driver's License"
        DOD_ID = 'DOD', 'DoD ID'
        SOCIAL_SECURITY = 'SSN', 'Social Security Card' # Be careful storing SSN
        PASSPORT = 'PASS', 'Passport'
        OTHER = 'OTH', 'Other'

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    identification_type = models.CharField(
        max_length=4,
        choices=IdentificationTypeChoices.choices,
        blank=True
    )
    identification_number = models.CharField(max_length=100, blank=True, help_text="Number associated with the ID type")
    is_approved = models.BooleanField(default=False, help_text="Has the tenant passed screening?")
    date_approved = models.DateField(null=True, blank=True, help_text="Date the tenant was approved")
    move_in_date = models.DateField(null=True, blank=True, help_text="Date the tenant officially moved in")
    # A tenant lives in one property at a time. Null=True means they might be approved but not yet placed, or moved out.
    # SET_NULL: If property is deleted, keep tenant record but remove link. Consider PROTECT if you never want to delete a property with tenants.
    property = models.ForeignKey(
        Property,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tenants',
        help_text="The property this tenant currently occupies (if any)"
    )

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
