from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import View
from django.urls import reverse
from .common import hash_it
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
                new_user.password = hash_it(password1)
                new_user.save()
                return redirect(reverse('login'))
        else:
            return render(request, 'blog/register.html', locals())


class Login(View):
    def get(self, request):
        if request.session.get('is_login'):
            return redirect(reverse('index'))
        return render(request, 'blog/login.html')

    def post(self, request):
        login_form = forms.LoginForm(request.POST)
        message = '用户名密码错误！'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user = models.User.objects.filter(username=username)
            if user:
                hash_password = hash_it(password)
                if hash_password != user.password:
                    message = '密码错误！'
                    return render(request, 'blog/login.html', locals())
                else:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.username
                    # login_user = user
                    return render(request, 'blog/index.html', locals())
            else:
                message = '用户不存在！'
                return render(request, 'blog/login.html', locals())
        else:
            return render(request, 'blog/login.html', locals())


def logout(request):
    if request.method == 'GET':
        if not request.session.get('is_login'):
            return redirect(reverse('login'))
        request.session.flush()
        return redirect(reverse('login'))

