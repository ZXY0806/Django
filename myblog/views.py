from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django.urls import reverse
from . import common
from . import models
from . import forms
from datetime import datetime, timedelta
import json, logging
from itertools import chain
# Create your views here.

logger = logging.getLogger('console')


def index(request):
    if request.method == 'GET':
        queryset = models.Blog.objects.all()
        page = common.generate_page(request, queryset, 25)
        return render(request, 'blog/index.html', locals())


class Register(View):
    def get(self, request):
        if request.session.get('is_login'):
            return redirect('blog/index/')
        return render(request, 'blog/register.html')

    def post(self, request):
        data = json.loads(request.body.decode())
        register_form = forms.RegisterForm(data)
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            email = register_form.cleaned_data.get('email')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            if password1 != password2:
                res = {'error': 'bad-request', 'message': '两次输入的密码不同！'}
                return JsonResponse(res)
            # 此处应添加用户名校验，只能为大小写字母、数字或下划线，不能为汉字，避免url为汉字时报错
            same_name_user = models.User.objects.filter(username=username)
            if same_name_user:
                res = {'error': 'bad-request', 'message': '用户名已经存在！'}
                return JsonResponse(res)
            same_email_user = models.User.objects.filter(email=email)
            if same_email_user:
                res = {'error': 'bad-request', 'message': '该邮箱已经被注册了！'}
                return JsonResponse(res)

            new_user = models.User()
            new_user.username = username
            new_user.email = email
            new_user.password = common.hash_it(password1)
            new_user.save()
            confirm_code = common.generate_confirm_string(new_user)
            res = common.send_confirm_email(confirm_code, email)
            print(res)
            res = {}
            return JsonResponse(res)
        else:
            res = {'error': 'bad-request', 'message': '请检查输入的内容！'}
            return JsonResponse(res)


def confirm(request):
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
    else:
        message = '欢迎注册，请前往邮箱确认！'
        return render(request, 'blog/confirm.html', locals())


class Login(View):
    def get(self, request):
        if request.session.get('is_login'):
            return redirect(reverse('index'))
        request.session['return_url'] = request.GET.get('returnUrl')
        return render(request, 'blog/login.html')

    def post(self, request):
        data = json.loads(request.body.decode())
        login_form = forms.LoginForm(data)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            try:
                user = models.User.objects.get(username=username)
            except models.User.DoesNotExist:
                res = {'error': 'bad-request', 'message': '用户名错误！'}
                return JsonResponse(res)
            except models.User.MultipleObjectsReturned:
                res = {'error': 'bad-request', 'message': '用户名错误！'}
                logger.warning('用户名不唯一！！！')
                return JsonResponse(res)
            if not user.has_confirmed:
                res = {'error': 'bad-request', 'message': '该用户尚未确认，请邮件确认后登录！'}
                return JsonResponse(res)
            hash_password = common.hash_it(password)
            if hash_password != user.password:
                res = {'error': 'bad-request', 'message': '密码错误！'}
                return JsonResponse(res)
            else:
                request.session['is_login'] = True
                request.session['username'] = user.username
                return_url = request.session.get('return_url')
                if return_url:
                    res = {'return_url': return_url}
                    return JsonResponse(res)
                res = {}
                return JsonResponse(res)
        else:
            res = {'error': 'bad-request', 'message': '用户名密码错误'}
            return JsonResponse(res)


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
            blog.readers += 1
            blog.save()
            return render(request, 'blog/blog.html', locals())
        except models.Blog.DoesNotExist:
            return render(request, 'blog/404.html')

    def post(self, request):
        pass


class Comment(View):
    def get(self, request):
        pass

    def post(self, request, blog_id):
        if not request.session.get('is_login'):
            return redirect(reverse('login'))
        content = request.POST.get('content').strip()
        parent_id = request.POST.get('parent_id')
        parent = None
        if not content:
            res = {'error': '评论内容不能为空！'}
            return HttpResponse(json.dumps(res), content_type='application/json')
        if parent_id:
            parents = models.Comment.objects.filter(pk=parent_id)
            if parents:
                parent = parents[0]
        username = request.session.get('username')
        try:
            blog = models.Blog.objects.get(pk=blog_id)
        except models.Blog.DoesNotExist:
            logger.error('blog_id不存在！！！')
            raise
        # comment = models.Comment.objects.create(content=content, user=user, blog=blog, parent=parent)
        # blog.comments += 1
        # blog.save()
        # return HttpResponse(json.dumps(comment), content_type='application/json')


class MyBlog(View):
    def get(self, request, username):
        try:
            user = models.User.objects.get(username=username)
        except models.User.DoesNotExist:
            return render(request, 'blog/404.html')
        except models.User.MultipateObjectsReturned:
            logger.error('用户名不唯一')
            raise
        common.get_relation(request, user)
        blogs = user.blog_set.all()
        page = common.generate_page(request, blogs, 25)
        return render(request, 'blog/myblog.html', locals())

    def post(self, request):
        pass


class Resume(View):
    def get(self, request, username):
        if not request.session.get('is_login'):
            return redirect(reverse('login'))
        try:
            user = models.User.objects.get(username=username)
        except models.DoesNotExist:
            logging.warning('用户名不存在！！！')
            return redirect(reverse('index'))
        except models.MultipleObjectsReturned:
            logging.error('用户名不唯一！！！')
            raise
        common.get_relation(request, user)
        follows = user.as_follower.all().values('followed')[:9]
        fans = user.as_followed.all().values('follower')[:9]
        blogs = user.blog_set.all()
        blogs_page = common.generate_page(request, blogs, 20)
        return render(request, 'blog/resume.html', locals())

    def post(self, request):
        pass


class Relation(View):
    def get(self, request):

        pass

    def post(self, request):
        pass


def hot(request):
    queryset = models.Blog.objects.order_by('-readers')
    page = common.generate_page(request, queryset, 25)
    return render(request, 'blog/hot.html', locals())


def following(request):
    if not request.session.get('is_login'):
        return redirect(reverse('login'))
    user = models.User.objects.get(username=request.session.get('username'))
    relations = user.as_follower.all()
    queryset = []
    for rla in relations:
        blogs = rla.followed.blog_set.all()
        queryset = chain(queryset, blogs)
    page = common.generate_page(request, queryset, 25)
    return render(request, 'blog/following.html', locals())
    # 开发指针，调试关注页


def mycommented(request):
    pass

