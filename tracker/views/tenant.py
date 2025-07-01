# tracker/views/tenant.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import ProtectedError


from tracker.models import Tenant
from tracker.forms import TenantForm


# Tenants view
@login_required
@permission_required('tracker.view_tenant', login_url='/login/', raise_exception=True)
def tenant_list(request):
    tenants = Tenant.objects.all().order_by('last_name', 'first_name')
    context = {'tenants': tenants}
    return render(request, 'tracker/tenant_list.html', context)


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
