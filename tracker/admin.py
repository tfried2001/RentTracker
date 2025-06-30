# tracker/admin.py
from django.contrib import admin
from .models import LLC, Property, Tenant, Payment, PropertyFinancialHistory

@admin.register(LLC)
class LLCAdmin(admin.ModelAdmin):
    list_display = ('name', 'creation_date', 'last_filing_date', 'filing_current')
    search_fields = ('name',)
    list_editable = ('filing_current',)

class PropertyFinancialHistoryInline(admin.TabularInline):
    model = PropertyFinancialHistory
    extra = 0 # Don't show empty forms for adding new history records
    readonly_fields = ('field_name', 'old_value', 'new_value', 'date_changed', 'changed_by')
    can_delete = False # History should be immutable
    verbose_name = "Financial History"
    verbose_name_plural = "Financial History"

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'llc', 'status', 'rent_amount', 'bedrooms', 'bathrooms')
    list_filter = ('status', 'llc', 'bedrooms', 'bathrooms')
    search_fields = ('street_number', 'street_name', 'vin', 'llc__name')
    raw_id_fields = ('llc',) # Better UI for selecting LLC if you have many
    inlines = [PropertyFinancialHistoryInline]

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'property', 'phone_number', 'is_approved', 'move_in_date')
    list_filter = ('is_approved', 'property__llc', 'property__status') # Filter by property status or LLC
    search_fields = ('first_name', 'last_name', 'phone_number', 'property__street_name', 'property__street_number')
    raw_id_fields = ('property',) # Better UI for selecting Property

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'amount', 'payment_date', 'tenant', 'property')
    list_filter = ('payment_date', 'property__llc', 'tenant')
    search_fields = ('tenant__first_name', 'tenant__last_name', 'property__street_name', 'property__street_number', 'notes')
    raw_id_fields = ('tenant', 'property') # Better UI for selecting Tenant/Property
    date_hierarchy = 'payment_date' # Adds date drilldown navigation

@admin.register(PropertyFinancialHistory)
class PropertyFinancialHistoryAdmin(admin.ModelAdmin):
    list_display = ('property', 'field_name', 'old_value', 'new_value', 'date_changed', 'changed_by')
    list_filter = ('field_name', 'date_changed', 'property__llc')
    search_fields = ('property__street_name', 'changed_by__username')
    raw_id_fields = ('property', 'changed_by')
    list_per_page = 25
