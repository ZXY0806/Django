from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import View
from django.urls import reverse
from . import models
from . import forms
# Create your views here.


def index(request):
    return HttpResponse('HelloWorld')


class Register(View):
    def get(self, request):
        if request.session.get('is_login'):
            return redirect('blog/index/')
        return render(request, 'blog/register.html')

    def post(self, request):
        register_form = forms.RegisterForm(request.POST)
        message = '请检查填写的内容！'
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            email = register_form.cleaned_data.get('email')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            if password1 != password2:
                message = '两次输入的密码不同！'
                return render(request, 'blog/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(username=username)
                if same_name_user:
                    message = '用户名已经存在'
                    return render(request, 'blog/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱已经被注册了！'
                    return render(request, 'blog/register.html', locals())

                new_user = models.User()
                new_user.username = username
                new_user.email = email
                new_user.password = password2

        else:
            return render(request, 'blog/register.html', locals())
        

def login(request):
    pass
    return render(request, 'blog/login.html')


def logout(request):
    pass
    return redirect('/login/')

