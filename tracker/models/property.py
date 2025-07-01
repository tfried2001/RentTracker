# tracker/models/property.py
from django.db import models
from tracker.models import LLC
from django.core.validators import MinValueValidator
from decimal import Decimal


class Property(models.Model):
    """Represents a rentable mobile home property."""
    class StatusChoices(models.TextChoices):
        OCCUPIED = 'OCC', 'Occupied'
        VACANT = 'VAC', 'Vacant'
        OFFICE = 'OFF', 'Office'
        LOT_VACANT = 'LOT', 'Lot Vacant'
        OTHER = 'OTH', 'Other'

    llc = models.ForeignKey(
        LLC,
        on_delete=models.PROTECT, # Prevent deleting LLC if it owns properties
        related_name='properties',
        help_text="The LLC that owns this property"
    )
    street_number = models.CharField(max_length=20, help_text="e.g., '123', '456A'")
    street_name = models.CharField(max_length=150, help_text="e.g., 'Main St', 'Elm Ave Lot 5'")
    date_purchased = models.DateField(null=True, blank=True, help_text="Date the property/home was acquired")
    size = models.CharField(max_length=50, blank=True, help_text="Description of size (e.g., '14x60', 'Double Wide', '1000 sq ft')")
    status = models.CharField(
        max_length=3,
        choices=StatusChoices.choices,
        default=StatusChoices.VACANT,
        help_text="Current status of the property"
    )
    rent_amount = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Monthly rent amount in dollars"
    )
    home_payment = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Monthly home mortgage/payment (if any) in dollars"
    )
    lot_payment = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Monthly lot rent/payment (if applicable) in dollars"
    )
    make = models.CharField(max_length=100, blank=True, help_text="Manufacturer of the mobile home")
    year = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Year the mobile home was manufactured")
    vin = models.CharField(max_length=50, blank=True, unique=True, null=True, help_text="Vehicle Identification Number (VIN) of the mobile home") # Unique might be too strict if you don't always have it
    security_deposit = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Required security deposit amount in dollars"
    )
    bedrooms = models.PositiveSmallIntegerField(default=1, help_text="Number of bedrooms")
    bathrooms = models.DecimalField(
        max_digits=3, decimal_places=1, default=Decimal('1.0'),
        validators=[MinValueValidator(Decimal('0.5'))],
        help_text="Number of bathrooms (e.g., 1.0, 1.5, 2.0)"
    )
    power_provider = models.CharField(max_length=100, blank=True, help_text="Name of the electric utility provider")
    water_provider = models.CharField(max_length=100, blank=True, help_text="Name of the water utility provider")

    class Meta:
        verbose_name_plural = "Properties"
        ordering = ['llc', 'street_number', 'street_name']
        # Unique constraint for address within an LLC (optional but good)
        unique_together = (('llc', 'street_name', 'street_number'),)

    def __str__(self):
        return f"{self.street_number} {self.street_name} ({self.llc.name})"

class PropertyFinancialHistory(models.Model):
    """Tracks changes to financial fields on the Property model."""
    class TrackedField(models.TextChoices):
        RENT_AMOUNT = 'rent_amount', 'Rent Amount'
        HOME_PAYMENT = 'home_payment', 'Home Payment'
        LOT_PAYMENT = 'lot_payment', 'Lot Payment'

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE, # If property is deleted, its history is deleted too.
        related_name='financial_history'
    )
    field_name = models.CharField(
        max_length=20,
        choices=TrackedField.choices,
        help_text="The financial field that was changed."
    )
    old_value = models.DecimalField(max_digits=8, decimal_places=2, help_text="The value before the change.")
    new_value = models.DecimalField(max_digits=8, decimal_places=2, help_text="The value after the change.")
    date_changed = models.DateTimeField(auto_now_add=True, help_text="When the change was made.")
    changed_by = models.ForeignKey(
        'auth.User', # Use string to avoid circular import issues
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The user who made the change."
    )

    class Meta:
        verbose_name_plural = "Property Financial History"
        ordering = ['-date_changed']

    def __str__(self):
        return f"Change on {self.property} ({self.get_field_name_display()}) on {self.date_changed.strftime('%Y-%m-%d')}"
