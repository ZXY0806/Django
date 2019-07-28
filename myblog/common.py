import hashlib
from . import models
import time
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def hash_it(str, salt='this is a salt'):
    h1 = hashlib.sha256()
    str += salt
    h1.update(str.encode())
    return h1.hexdigest()


def generate_confirm_string(user):
    now = time.strftime('%Y-%m-%d %H-%M-%S')
    code = hash_it(user.username, salt=now)
    models.ConfirmString.objects.create(user=user, code=code)
    return code


def send_confirm_email(confirm_code, email):
    subject = '注册确认邮件'
    text_content = '如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'
    html_content = '''
    <p>感谢注册,<a href=http://{}/blog/confirm/?code={}>点击确认</a>注册,此链接有效期为{}天！</p>
    '''.format(settings.WEBSITE, confirm_code, settings.CONFIRM_DAYS)
    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    email.attach_alternative(html_content, 'text/html')
    res = email.send()
    return res


def generate_page(request, query_set, size):
    paginator = Paginator(query_set, size)
    page_num = request.GET.get('page')
    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page


def get_relation(request, user):
    request.session['relation'] = 'unfollow'
    if request.session.get('is_login'):
        if request.session['username'] != user.username:
            follower = models.User.objects.get(pk=request.session['user_id'])
            relation = user.as_followed.filter(follower=follower, followed=user)
            if relation:
                request.session['relation'] = 'followed'
        else:
            request.session['relation'] = 'self'


def add_indents_for_comments(comments):
    res = []
    def recursive_search(children, indent):
        for c in children:
            c.indent = indent
            res.append(c)
            children = c.children.all()
            if children:
                recursive_search(children, indent+40)
    recursive_search(comments, 0)
    return res

