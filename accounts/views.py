from django.contrib import auth
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView, View
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

# Create your views here.
def index(request):
    return render(request, 'accounts/index.html')


class Create_account(CreateView):
    def post(self, request, *args, **kwargs):
        form =  UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect(reverse('accounts:index'))
        return render(request, 'accounts/create.html', {'form': form})

    
    def get(self, request, *args, **kwargs):
        form = UserCreationForm()
        if 'next' in request.GET.keys():
            nextPath = request.GET['next']
        else:
            nextPath = "/accounts/"
        return render(request, 'accounts/create.html', {'form': form, "next": nextPath})

create_account = Create_account.as_view()


class Login_account(View):
    def post(self, request, *arg, **kwargs):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            user = User.objects.get(username=username)
            login(request, user)
            return redirect(request.POST["next"])
        return render(request, 'accounts/login.html', {'form': form})

    def get(self, request, *args, **kwargs):
        form = AuthenticationForm()
        if 'next' in request.GET.keys():
            nextPath = request.GET['next']
        else:
            nextPath = "/accounts/"
        return render(request, 'accounts/login.html', {'form': form, 'next': nextPath})


login_account = Login_account.as_view()

