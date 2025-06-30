# tracker/forms.py
from django import forms
import datetime
from .models import LLC, Property, Tenant, Payment

class LLCForm(forms.ModelForm):
    class Meta:
        model = LLC
        fields = '__all__' # Include all fields from the LLC model
        widgets = {
            'creation_date': forms.DateInput(attrs={'type': 'date'}),
            'last_filing_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_year = datetime.date.today().year
        if 'filing_current' in self.fields:
            self.fields['filing_current'].label = f"Filed for {current_year}"

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = '__all__' # Include all fields from the Property model
        widgets = {
            'date_purchased': forms.DateInput(attrs={'type': 'date'}),
        }

class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = '__all__' # Include all fields from the Tenant model
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_approved': forms.DateInput(attrs={'type': 'date'}),
            'move_in_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__' # Include all fields from the Payment model
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PropertyBulkUpdateForm(forms.Form):
    """
    A form for updating the status of multiple properties at once.
    """
    status = forms.ChoiceField(
        choices=Property.StatusChoices.choices,
        required=True,
        label="Set status for all selected properties to"
    )