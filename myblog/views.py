from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import View
from django.urls import reverse
from .models import User
from . import forms
# Create your views here.


def index(request):
    return HttpResponse('HelloWorld')


class Register(View):
    def get(self, request):
        return render(request, 'blog/register.html')

    def post(self, request):
        register_form = forms.RegisterForm(request.POST)
        if register_form.is_valid():
            pass
        else:
            message = '请检查填写的内容！'
            return render(request, reverse('register'), locals())
        

def login(request):
    pass
    return render(request, 'blog/login.html')


def logout(request):
    pass
    return redirect('/login/')

