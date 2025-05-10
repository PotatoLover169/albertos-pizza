from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "You don't have staff permissions to login.")
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'login/login.html')

@login_required
def dashboard_view(request):
    return redirect('dashboard')  # Redirect to administrator dashboard

def logout_view(request):
    logout(request)
    return redirect('login')

def home_view(request):
    return render(request, 'login/home.html')
