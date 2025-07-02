# tracker/views/llc.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import ProtectedError

from ..models import LLC
from ..forms import LLCForm

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
    context = {
        'object': llc,
        'object_type': 'LLC',
        'cancel_url': 'tracker:llc_list'
    }
    return render(request, 'tracker/generic_confirm_delete.html', context)
