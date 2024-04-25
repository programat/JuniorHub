# users/views.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/vacancies')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def profile(request):
    return render(request, 'users/profile.html')


@login_required
def profile(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        form = CustomUserCreationForm(instance=request.user)
        return render(request, 'users/profile.html', {'form': form})


def login_view(request):
    error_message = ''
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/vacancies')
        else:
            error_message = 'Неверное имя пользователя или пароль'
    return render(request, 'users/login.html', {'error_message': error_message})


def logout_view(request):
    logout(request)
    return redirect('login')
