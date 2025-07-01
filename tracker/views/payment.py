# tracker/views/payment.py
from django.shortcuts import render, redirect, get_object_or_404 # Import redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import ProtectedError


from tracker.models import Payment
from tracker.forms import PaymentForm


# Payments view
@login_required
@permission_required('tracker.view_payment', login_url='/login/', raise_exception=True)
def payment_list(request):
    payments = Payment.objects.select_related('tenant', 'property').all().order_by('-payment_date')
    context = {'payments': payments}
    return render(request, 'tracker/payment_list.html', context)


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
