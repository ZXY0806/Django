from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django.urls import reverse
from django.conf import settings
from . import common
from . import models
from . import forms
from datetime import datetime, timedelta
import json, logging
from itertools import chain
import os
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
            return redirect(reverse('index'))
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
        if request.GET.get('returnUrl'):
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
                request.session['user_image'] = user.image.url
                request.session['user_id'] = user.id
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
    def get(self, request, username, blog_id):
        try:
            blog = models.Blog.objects.get(pk=blog_id)
            queryset = models.Comment.objects.filter(blog_id=blog_id, parent=None)
            comments = common.add_indents_for_comments(queryset)
            blog.readers += 1
            blog.save()
            return render(request, 'blog/blog.html', locals())
        except models.Blog.DoesNotExist:
            return render(request, 'blog/404.html')

    def post(self, request):
        pass


class EditBlog(View):
    def get(self, request):
        if not request.session.get('is_login'):
            return redirect(reverse('login'))
        return_url = request.META.get('HTTP_REFERER', '/blog/')
        request.session['return_url'] = return_url
        form = forms.BlogForm()
        blog_id = request.GET.get('blog_id')
        if blog_id:
            blog = models.Blog.objects.get(pk=int(blog_id))
            if blog.user.username != request.session.get('username'):
                return reverse(request, 'blog/404.html')
            data = {
                'name': blog.name,
                'digest': blog.digest,
                'content': blog.content,
            }
            form = forms.BlogForm(data)
        return render(request, 'blog/edit_blog.html', locals())

    def post(self, request):
        if not request.session.get('is_login'):
            return redirect(reverse('login'))
        form = forms.BlogForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('name')
            if not title:
                message = '请输入文章标题'
                return render(request, 'blog/edit_blog.html', locals())
            digest = form.cleaned_data.get('digest')
            if not digest:
                message = '请输入文章摘要'
                return render(request, 'blog/edit_blog.html', locals())
            content = form.cleaned_data.get('content')
            if not content:
                message = '请输入文章内容'
                return render(request, 'blog/edit_blog.html', locals())
            if request.POST.get('blog_id'):
                blog = models.Blog.objects.get(pk=int(request.POST.get('blog_id')))
                blog.name = title
                blog.digest = digest
                blog.content = content
                blog.save()
                return redirect(reverse('blog', kwargs={'username': request.session.get('username'), 'blog_id': blog.id}))
            else:
                user = models.User.objects.get(pk=request.session.get('user_id'))
                blog = models.Blog.objects.create(name=title, digest=digest, content=content, user=user)
                return redirect(reverse('blog', kwargs={'username': request.session.get('username'), 'blog_id': blog.id}))
        else:
            message = '请检查输入内容'
            return render(request, 'blog/edit_blog.html', locals())


class DeleteBlog(View):
    def get(self, request):
        if not request.session.get('is_login'):
            return redirect(reverse('login'))
        blog_id = request.GET.get('blog_id')
        if not blog_id:
            res = {'error': 'bad-request', 'message': '文章不存在！'}
            return JsonResponse(res)
        blog = models.Blog.objects.get(pk=int(blog_id))
        blog.delete()
        res = {}
        return JsonResponse(res)

    def post(self, request):
        pass


class ManageBlogs(View):
    def get(self, request):
        if not request.session.get('is_login'):
            return redirect(reverse('login'))
        query_set = models.Blog.objects.filter(user__username=request.session.get('username'))
        page = common.generate_page(request, query_set, 25)
        return render(request, 'blog/manage_blogs.html', locals())

    def post(self, request):
        pass


class Comment(View):
    def get(self, request):
        pass

    def post(self, request, username, blog_id):
        if not request.session.get('is_login'):
            return redirect(reverse('login'))
        data = json.loads(request.body.decode())
        content = data.get('content')
        if content:
            content = content.strip()
        if not content:
            res = {'error': 'bad-request', 'message': '评论内容不能为空！'}
            return JsonResponse(res)
        parent_id = data.get('parent_id')
        if parent_id:
            parent = models.Comment.objects.get(pk=parent_id)
        else:
            parent = None
        blog = models.Blog.objects.get(pk=blog_id)
        user = models.User.objects.get(pk=request.session.get('user_id'))
        comment = models.Comment.objects.create(content=content, user=user, blog=blog, parent=parent)
        res = {}
        return JsonResponse(res)


class MyBlog(View):
    def get(self, request, username):
        user = models.User.objects.get(username=username)
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
        user = models.User.objects.get(username=username)
        common.get_relation(request, user)
        follows = user.as_follower.all().values('followed')[:9]
        fans = user.as_followed.all().values('follower')[:9]
        blogs = user.blog_set.all()
        blogs_page = common.generate_page(request, blogs, 20)
        return render(request, 'blog/resume.html', locals())

    def post(self, request):
        pass


class UploadPhoto(View):
    def get(self, request, username):
        if not request.session.get('is_login'):
            return redirect(reverse('login'))
        user = models.User.objects.get(pk=request.session.get('user_id'))
        return render(request, 'blog/upload_photo.html', locals())

    def post(self, request, username):
        if not request.session.get('is_login'):
            return redirect(reverse('login'))
        file_obj = request.FILES.get('file_obj')
        path = os.path.join(settings.MEDIA_ROOT, 'img/', file_obj.name)
        with open(path, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        user = models.User.objects.get(pk=request.session.get('user_id'))
        user.image = 'img/' + file_obj.name
        user.save()
        request.session['user_image'] = user.image.url
        res = {}
        return JsonResponse(res)


class AccountSet(View):
    def get(self, request, username):
        if not request.session.get('is_login'):
            return redirect(reverse('login'))
        user = models.User.objects.get(pk=request.session.get('user_id'))
        return render(request, 'blog/account_set.html', locals())

    def post(self, request):
        pass


class UserName(View):
    def get(self, request):
        pass

    def post(self, request):
        if not request.session.get('is_login'):
            return redirect(reverse('login'))
        data = json.loads(request.body.decode())
        new_username = data.get('username')
        if new_username:
            new_username = new_username.strip()
        if not new_username:
            res = {'error': 'bad-request', 'message': '用户名不能为空！'}
            return JsonResponse(res)
        if new_username == request.session.get('username'):
            res = {'error': 'bad-request', 'message': '用户名与原用户名不能相同！'}
            return JsonResponse(res)
        same_name_user = models.User.objects.filter(username=new_username)
        if same_name_user:
            res = {'error': 'bad-request', 'message': '用户名已被注册！'}
            return JsonResponse(res)
        user = models.User.objects.get(pk=request.session.get('user_id'))
        user.username = new_username
        user.save()
        request.session['username'] = new_username
        res = {}
        request.session.flush()
        print('jin')
        return JsonResponse(res)


class Password(View):
    def get(self, request):
        pass

    def post(self, request):
        if not request.session.get('is_login'):
            return redirect(reverse('login'))
        data = json.loads(request.body.decode())
        old_pwd = data.get('old_pwd', '').strip()
        password1 = data.get('password1', '').strip()
        password2 = data.get('password2', '').strip()
        if not old_pwd or not password1 or not password2:
            res = {'error': 'bad-request', 'message': '密码不能为空！'}
            return JsonResponse(res)
        if password1 != password2:
            res = {'error': 'bad-request', 'message': '两次密码输入不同！'}
            return JsonResponse(res)
        user = models.User.objects.get(pk=request.session.get('user_id'))
        hash_old_pwd = common.hash_it(old_pwd)
        if hash_old_pwd != user.password:
            res = {'error': 'bad-request', 'message': '旧密码输入错误！'}
            return JsonResponse(res)
        hash_new_pwd = common.hash_it(password1)
        user.password = hash_new_pwd
        user.save()
        res = {}
        request.session.flush()
        return JsonResponse(res)


class Email(View):
    def get(self, request):
        pass

    def post(self, request):
        if not request.session.get('is_login'):
            return redirect(reverse('login'))
        data = json.loads(request.body.decode())
        password = data.get('password', '').strip()
        new_email = data.get('email', '').strip()
        if not password:
            res = {'error': 'bad-request', 'message': '账户密码不能为空！'}
            return JsonResponse(res)
        if not new_email:
            res = {'error': 'bad-request', 'message': '注册邮箱不能为空！'}
            return JsonResponse(res)
        same_email_user = models.User.objects.filter(email=new_email)
        if same_email_user:
            res = {'error': 'bad-request', 'message': '该邮箱已被注册！'}
            return JsonResponse(res)
        user = models.User.objects.get(pk=request.session.get('user_id'))
        hash_password = common.hash_it(password)
        if hash_password != user.password:
            res = {'error': 'bad-request', 'message': '账户密码错误！'}
            return JsonResponse(res)
        user.email = new_email
        user.has_confirmed = False
        user.save()
        confirm_code = common.generate_confirm_string(user)
        common.send_confirm_email(confirm_code, new_email)
        res = {}
        request.session.flush()
        return JsonResponse(res)


def follow(request, username):
    return_url = request.META.get('HTTP_REFERER', '/blog/')
    if not request.session.get('is_login'):
        request.session['return_url'] = return_url
        return redirect(reverse('login'))
    follower = models.User.objects.get(pk=request.session.get('user_id'))
    followed = models.User.objects.get(username=username)
    models.Relation.objects.create(follower=follower, followed=followed)
    follower.follow_num += 1
    follower.save()
    followed.fans_num += 1
    followed.save()
    return redirect(return_url)


def unfollow(request, username):
    return_url = request.META.get('HTTP_REFERER', '/blog/')
    if not request.session.get('is_login'):
        request.session['return_url'] = return_url
        return redirect(reverse('login'))
    follower = models.User.objects.get(pk=request.session.get('user_id'))
    followed = models.User.objects.get(username=username)
    rela = models.Relation.objects.get(follower=follower, followed=followed)
    rela.delete()
    follower.follow_num -= 1
    follower.save()
    followed.fans_num -= 1
    followed.save()
    return redirect(return_url)


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
    queryset = list(queryset)
    page = common.generate_page(request, queryset, 25)
    return render(request, 'blog/following.html', locals())


def mycommented(request):
    if not request.session.get('is_login'):
        return redirect(reverse('login'))
    queryset = models.Blog.objects.filter(comment__user__username=request.session.get('username')).distinct()
    page = common.generate_page(request, queryset, 25)
    return render(request, 'blog/commented.html', locals())



