# tracker/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import LLC


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

