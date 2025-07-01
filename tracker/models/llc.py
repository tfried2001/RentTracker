# tracker/models/llc.py
from django.db import models
import datetime # Import datetime


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
