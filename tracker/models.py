# tracker/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import datetime # Import datetime
from dateutil.relativedelta import relativedelta # Import relativedelta

class LLC(models.Model):
    """Represents a Limited Liability Company that owns properties."""
    name = models.CharField(max_length=200, unique=True, help_text="Name of the LLC")
    creation_date = models.DateField(help_text="Date the LLC was officially created")
    last_filing_date = models.DateField(
        null=True, #Allow null if the first filing hasn't happened
        blank=True, #Allow blank in forms/admin
        help_text="Date of the last required filing (e.g., annual report)")
    filing_current = models.BooleanField(
        default=False,
        help_text="Has the annual filing for the current year been completed?"
    )

    class Meta:
        verbose_name = "LLC"
        verbose_name_plural = "LLCs"
        ordering = ['name']

    def __str__(self):
        return self.name
    
    @property
    def filing_status(self):
        """
        Determines the filing status based on the filing_current flag
        and the annual April 15th deadline.

        - green: The filing for the current year is marked as complete.
        - yellow: The filing is not complete, and the deadline is approaching.
        - red: The filing is not complete, and the deadline has passed.

        Returns:
            str: 'green', 'yellow', or 'red'
        """
        if self.filing_current:
            return 'green'

        today = datetime.date.today()
        deadline = datetime.date(today.year, 4, 15)

        if today >= deadline:
            return 'red'
        else:  # today is before the deadline
            return 'yellow'


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


class Payment(models.Model):
    """Represents a single payment made by a tenant towards a property."""
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.PROTECT, # Keep payment history even if the tenant record is somehow deleted? Or CASCADE? PROTECT is safer.
        related_name='payments',
        help_text="The tenant who made the payment"
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.PROTECT, # Keep payment history even if property record is deleted.
        related_name='payments',
        help_text="The property the payment is for"
    )
    payment_date = models.DateField(help_text="Date the payment was received")
    amount = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))], # Payments should be positive
        help_text="Amount of the payment in dollars"
    )
    notes = models.TextField(blank=True, help_text="Optional notes (e.g., check number, payment method, period covered)")

    class Meta:
        ordering = ['-payment_date', 'tenant'] # Show most recent first

    def __str__(self):
        return f"Payment: ${self.amount} by {self.tenant} on {self.payment_date} for {self.property.street_number} {self.property.street_name}"


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
