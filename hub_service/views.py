from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from hub_service.forms import SignUpForm


def index(request):
    return render(request, 'hub_service/index.html')


def advertisement(request):
    return render(request, 'hub_service/advertisement.html')


@login_required
def profile(request):
    return render(request, 'hub_service/profile.html')


def about(request):
    return render(request, 'hub_service/about.html')


def contact(request):
    return render(request, 'hub_service/contact.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
