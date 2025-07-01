# tracker/views/property.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import ProtectedError

from tracker.models import Property
from tracker.forms import PropertyForm, PropertyBulkUpdateForm


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