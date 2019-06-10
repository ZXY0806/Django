from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import View
from .models import User
# Create your views here.


def index(request):
    return HttpResponse('HelloWorld')


class Register(View):
    def get(self, request):
        return render(request, 'blog/register.html')

    def post(self, request):
        email = request.POST.get('email').strip()
        name = request.POST.get('name').strip()
        password = request.POST.get('password').strip()




def login(request):
    pass
    return render(request, 'blog/login.html')


def logout(request):
    pass
    return redirect('/login/')

