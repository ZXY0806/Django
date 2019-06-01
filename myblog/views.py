from django.shortcuts import render,redirect
from django.http import HttpResponse

# Create your views here.


def index(request):
    return HttpResponse('HelloWorld')


def register(request):
    pass
    return render(request, 'blog/register.html')


def login(request):
    pass
    return render(request, 'blog/login.html')


def logout(request):
    pass
    return redirect('/login/')

