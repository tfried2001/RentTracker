# tracker/views.py
from django.shortcuts import render, redirect, get_object_or_404 # Import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required # Import login_required
from django.db import IntegrityError, transaction # For handling potential errors
from django.db.models import ProtectedError # To handle deletion protection

from .models import LLC, Property, Tenant, Payment # Import the LLC model
from .forms import LLCForm, PropertyForm, TenantForm, PaymentForm, PropertyBulkUpdateForm # Import the forms

# Public homepage view
def home(request):
    # You can pass context data to the template if needed
    context = {'message': "Welcome to RentTracker!"}
    return render(request, 'home.html', context)

# Dashboard view
@login_required
def dashboard(request):
    llcs = LLC.objects.all().order_by('name')
    context = {
        'user_first_name': request.user.first_name or request.user.username,
        'llcs': llcs, # <-- Add llcs to the context
    }
    return render(request, 'tracker/dashboard.html', context)

# LLCs view
@login_required
@permission_required('tracker.view_llc', login_url='/login/', raise_exception=True)
def llc_list(request):
    """Displays a list of all LLCs and their filing status."""
    llcs = LLC.objects.all().order_by('name') # Get all LLCs, ordered by name
    context = {
        'llcs': llcs,
    }
    return render(request, 'tracker/llc_list.html', context)

# Properties view
@login_required
@permission_required('tracker.view_property', login_url='/login/', raise_exception=True)
def property_list(request):
    """Displays a list of all properties."""
    properties = Property.objects.all().order_by('llc', 'street_number', 'street_name') # Get all properties, ordered by LLC, address
    context = {
        'properties': properties,
    }
    return render(request, 'tracker/property_list.html', context)

# Tenants view
@login_required
@permission_required('tracker.view_tenant', login_url='/login/', raise_exception=True)
def tenant_list(request):
    tenants = Tenant.objects.all().order_by('last_name', 'first_name')
    context = {'tenants': tenants}
    return render(request, 'tracker/tenant_list.html', context)

# Payments view
@login_required
@permission_required('tracker.view_payment', login_url='/login/', raise_exception=True)
def payment_list(request):
    payments = Payment.objects.select_related('tenant', 'property').all().order_by('-payment_date')
    context = {'payments': payments}
    return render(request, 'tracker/payment_list.html', context)



# --- LLC CRUD Views ---
@login_required
@permission_required('tracker.add_llc', login_url='/login/', raise_exception=True)
def llc_add(request):
    if request.method == 'POST':
        form = LLCForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"LLC '{form.cleaned_data['name']}' added successfully.")
                return redirect('tracker:llc_list')
            except IntegrityError: # Handle potential unique constraint errors
                 messages.error(request, "An LLC with this name already exists.")
            except Exception as e:
                 messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = LLCForm()
    context = {
        'form': form,
        'form_title': 'Add New LLC',
        'cancel_url': 'tracker:llc_list'
    }
    return render(request, 'tracker/generic_form.html', context)

@login_required
@permission_required('tracker.change_llc', login_url='/login/', raise_exception=True)
def llc_edit(request, pk):
    llc = get_object_or_404(LLC, pk=pk)
    if request.method == 'POST':
        form = LLCForm(request.POST, instance=llc)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"LLC '{llc.name}' updated successfully.")
                return redirect('tracker:llc_list')
            except IntegrityError:
                 messages.error(request, "An LLC with this name already exists.")
            except Exception as e:
                 messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = LLCForm(instance=llc)
    context = {
        'form': form,
        'form_title': f'Edit LLC: {llc.name}',
        'instance': llc,
        'cancel_url': 'tracker:llc_list'
    }
    return render(request, 'tracker/generic_form.html', context)

@login_required
@permission_required('tracker.delete_llc', login_url='/login/', raise_exception=True)
def llc_delete(request, pk):
    llc = get_object_or_404(LLC, pk=pk)
    if request.method == 'POST':
        try:
            llc_name = llc.name # Get name before deleting
            llc.delete()
            messages.success(request, f"LLC '{llc_name}' deleted successfully.")
            return redirect('tracker:llc_list')
        except ProtectedError:
            messages.error(request, f"Cannot delete LLC '{llc.name}' because it still owns properties. Please reassign or delete the properties first.")
            return redirect('tracker:llc_list') # Or redirect to llc detail page
        except Exception as e:
            messages.error(request, f"An error occurred while deleting: {e}")
            return redirect('tracker:llc_list')
    context = {'object': llc, 'object_type': 'LLC'}
    return render(request, 'tracker/generic_confirm_delete.html', context)


# --- Property CRUD Views ---
@login_required
@permission_required('tracker.add_property', login_url='/login/', raise_exception=True)
def property_add(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Property '{form.instance}' added successfully.")
                return redirect('tracker:property_list')
            except IntegrityError as e:
                 messages.error(request, f"Could not add property. Check for duplicate VIN or other constraints. Error: {e}")
            except Exception as e:
                 messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = PropertyForm()
    context = {
        'form': form,
        'form_title': 'Add New Property',
        'cancel_url': 'tracker:property_list'
    }
    return render(request, 'tracker/generic_form.html', context)

@login_required
@permission_required('tracker.change_property', login_url='/login/', raise_exception=True)
def property_edit(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=prop)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Property '{prop}' updated successfully.")
                return redirect('tracker:property_list')
            except IntegrityError as e:
                 messages.error(request, f"Could not update property. Check for duplicate VIN or other constraints. Error: {e}")
            except Exception as e:
                 messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = PropertyForm(instance=prop)
    context = {
        'form': form,
        'form_title': f'Edit Property: {prop}',
        'instance': prop,
        'cancel_url': 'tracker:property_list'
    }
    return render(request, 'tracker/generic_form.html', context)

@login_required
@permission_required('tracker.delete_property', login_url='/login/', raise_exception=True)
def property_delete(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        try:
            prop_str = str(prop)
            prop.delete()
            messages.success(request, f"Property '{prop_str}' deleted successfully.")
            return redirect('tracker:property_list')
        except ProtectedError:
            messages.error(request, f"Cannot delete Property '{prop}' because it has related Tenants or Payments. Please reassign or delete them first.")
            return redirect('tracker:property_list')
        except Exception as e:
            messages.error(request, f"An error occurred while deleting: {e}")
            return redirect('tracker:property_list')
    context = {'object': prop, 'object_type': 'Property'}
    return render(request, 'tracker/generic_confirm_delete.html', context)

@login_required
def property_bulk_action(request):
    if request.method != 'POST':
        messages.error(request, "This action can only be performed via POST.")
        return redirect('tracker:property_list')

    action = request.POST.get('action')
    selected_ids = request.POST.getlist('selected_properties')

    if not selected_ids:
        messages.warning(request, "You must select at least one property.")
        return redirect('tracker:property_list')

    # Check permissions for the chosen action
    if action == 'bulk_delete' and not request.user.has_perm('tracker.delete_property'):
        messages.error(request, "You do not have permission to delete properties.")
        return redirect('tracker:property_list')
    if action == 'bulk_update' and not request.user.has_perm('tracker.change_property'):
        messages.error(request, "You do not have permission to change properties.")
        return redirect('tracker:property_list')

    queryset = Property.objects.filter(pk__in=selected_ids)

    # --- Bulk Delete Logic ---
    if action == 'bulk_delete':
        if 'confirm_delete' in request.POST: # This is the confirmation step
            try:
                count = queryset.count()
                queryset.delete()
                messages.success(request, f"Successfully deleted {count} properties.")
            except ProtectedError:
                messages.error(request, "Deletion failed. Some properties have tenants or payments and cannot be deleted.")
            return redirect('tracker:property_list')
        
        # Render the confirmation page
        context = {'objects': queryset, 'object_type': 'Properties'}
        return render(request, 'tracker/generic_confirm_bulk_delete.html', context)

    # --- Bulk Update Logic ---
    if action == 'bulk_update':
        # This is the submission from the bulk update form
        if 'update_status_submit' in request.POST:
            form = PropertyBulkUpdateForm(request.POST)
            if form.is_valid():
                new_status = form.cleaned_data['status']
                updated_count = queryset.update(status=new_status)
                messages.success(request, f"Successfully updated {updated_count} properties to '{dict(Property.StatusChoices.choices)[new_status]}'.")
                return redirect('tracker:property_list')
        
        # This is the initial step, show the bulk update form
        form = PropertyBulkUpdateForm()
        context = {
            'form': form,
            'properties': queryset,
            'form_title': 'Bulk Update Property Status',
        }
        return render(request, 'tracker/property_bulk_update.html', context)

    messages.error(request, "No valid action was selected.")
    return redirect('tracker:property_list')

# --- Tenant CRUD Views ---
@login_required
@permission_required('tracker.add_tenant', login_url='/login/', raise_exception=True)
def tenant_add(request):
    if request.method == 'POST':
        form = TenantForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Tenant '{form.instance}' added successfully.")
                return redirect('tracker:tenant_list')
            except Exception as e:
                 messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = TenantForm()
    context = {
        'form': form,
        'form_title': 'Add New Tenant',
        'cancel_url': 'tracker:tenant_list'
    }
    return render(request, 'tracker/generic_form.html', context)

@login_required
@permission_required('tracker.change_tenant', login_url='/login/', raise_exception=True)
def tenant_edit(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk)
    if request.method == 'POST':
        form = TenantForm(request.POST, instance=tenant)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Tenant '{tenant}' updated successfully.")
                return redirect('tracker:tenant_list')
            except Exception as e:
                 messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = TenantForm(instance=tenant)
    context = {
        'form': form,
        'form_title': f'Edit Tenant: {tenant}',
        'instance': tenant,
        'cancel_url': 'tracker:tenant_list'
    }
    return render(request, 'tracker/generic_form.html', context)

@login_required
@permission_required('tracker.delete_tenant', login_url='/login/', raise_exception=True)
def tenant_delete(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk)
    if request.method == 'POST':
        try:
            tenant_str = str(tenant)
            tenant.delete()
            messages.success(request, f"Tenant '{tenant_str}' deleted successfully.")
            return redirect('tracker:tenant_list')
        except ProtectedError:
            messages.error(request, f"Cannot delete Tenant '{tenant}' because they have related Payments. Please delete the payments first.")
            return redirect('tracker:tenant_list')
        except Exception as e:
            messages.error(request, f"An error occurred while deleting: {e}")
            return redirect('tracker:tenant_list')
    context = {'object': tenant, 'object_type': 'Tenant'}
    return render(request, 'tracker/generic_confirm_delete.html', context)


# --- Payment CRUD Views ---
@login_required
@permission_required('tracker.add_payment', login_url='/login/', raise_exception=True)
def payment_add(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Payment added successfully.")
                return redirect('tracker:payment_list')
            except Exception as e:
                 messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = PaymentForm()
    context = {
        'form': form,
        'form_title': 'Add New Payment',
        'cancel_url': 'tracker:payment_list'
    }
    return render(request, 'tracker/generic_form.html', context)

@login_required
@permission_required('tracker.change_payment', login_url='/login/', raise_exception=True)
def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Payment updated successfully.")
                return redirect('tracker:payment_list')
            except Exception as e:
                 messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = PaymentForm(instance=payment)
    context = {
        'form': form,
        'form_title': f'Edit Payment: {payment}',
        'instance': payment,
        'cancel_url': 'tracker:payment_list'
    }
    return render(request, 'tracker/generic_form.html', context)

@login_required
@permission_required('tracker.delete_payment', login_url='/login/', raise_exception=True)
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        try:
            payment_str = str(payment)
            payment.delete()
            messages.success(request, f"Payment '{payment_str}' deleted successfully.")
            return redirect('tracker:payment_list')
        # No ProtectedError expected here based on current models, but keep general exception handling
        except Exception as e:
            messages.error(request, f"An error occurred while deleting: {e}")
            return redirect('tracker:payment_list')
    context = {'object': payment, 'object_type': 'Payment'}
    return render(request, 'tracker/generic_confirm_delete.html', context)


# Add views for LLCs, Properties, Tenants, Payments later
# Example for adding a property (you'll need a form and template later)
# @login_required
# @permission_required('tracker.add_property', login_url='/login/', raise_exception=True)
# def property_add(request):
#     # ... view logic for adding a property ...
#     pass

# Example for editing a property
# @login_required
# @permission_required('tracker.change_property', login_url='/login/', raise_exception=True)
# def property_edit(request, property_id):
#     # ... view logic for editing a specific property ...
#     pass

# Example for deleting a property
# @login_required
# @permission_required('tracker.delete_property', login_url='/login/', raise_exception=True)
# def property_delete(request, property_id):
#     # ... view logic for deleting a specific property ...
#     pass