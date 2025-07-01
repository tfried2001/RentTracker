# tracker/models/payment.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

from .tenant import Tenant
from .property import Property



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
