from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import View
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from . import common
from . import models
from . import forms
from datetime import datetime, timedelta

# Create your views here.


def index(request):
    if request.method == 'GET':
        queryset = models.Blog.objects.all()
        paginator = Paginator(queryset, 25)
        page_num = request.GET.get('page')
        try:
            page = paginator.page(page_num)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        return render(request, 'blog/index.html', locals())


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
            # 此处应添加用户名校验，只能为大小写字母、数字或下划线，不能为汉字，避免url为汉字时报错
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
            new_user.password = common.hash_it(password1)
            new_user.save()
            message = '欢迎注册，请前往邮箱确认！'
            confirm_code = common.generate_confirm_string(new_user)
            res = common.send_confirm_email(confirm_code, email)
            print(res)
            return render(request, 'blog/confirm.html', locals())
        else:
            return render(request, 'blog/register.html', locals())


def confirm(self, request):
    code = request.GET.get('code', None)
    if code:
        try:
            confirm_string = models.ConfirmString.objects.get(code=code)
            now = datetime.now()
            c_time = confirm_string.created_at
            if now > c_time + timedelta(days=1):
                message = '您的邮件已经过期！请重新注册!'
                confirm_string.user.delete()
                return render(request, 'blog/confirm.html', locals())
            else:
                confirm_string.user.has_confirmed = True
                confirm_string.user.save()
                confirm_string.delete()
                message = '感谢确认，请使用账户登录!'
                return render(request, 'blog/confirm.html', locals())
        except:
            message = '无效的确认请求!'
            return render(request, 'blog/confirm.html', locals())


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
                if not user.has_confirmed:
                    message = '该用户尚未确认，请邮件确认后登录！'
                    return render(request, 'blog/login.html', locals())
                hash_password = common.hash_it(password)
                if hash_password != user.password:
                    message = '密码错误！'
                    return render(request, 'blog/login.html', locals())
                else:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.username
                    request.session['user_image'] = user.image
                    # login_user = user
                    return redirect(reverse('index'))
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


class Blog(View):
    def get(self, request, blog_id):
        try:
            blog = models.Blog.objects.get(pk=blog_id)
            comments = models.Comment.objects.filter(blog_id=blog_id)
            return render(request, 'blog/blog.html', locals())
        except models.Blog.DoesNotExist:
            return render(request, 'blog/404.html')

    def post(self, requst):
        pass