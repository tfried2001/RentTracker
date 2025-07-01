# tracker/views/main.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    """
    Home page view.
    Redirects authenticated users to the dashboard.
    Renders a public landing page for anonymous users.
    """
    if request.user.is_authenticated:
        return redirect('tracker:dashboard')
    # You will need to create a 'tracker/home.html' template for your landing page
    return render(request, 'tracker/home.html')

@login_required
def dashboard(request):
    """
    Displays the main dashboard for logged-in users.
    """
    # You will need to create a 'tracker/dashboard.html' template
    return render(request, 'tracker/dashboard.html')