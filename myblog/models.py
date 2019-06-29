from django.db import models

# Create your models here.


class User(models.Model):
    # gender = (('male', '男'), ('female', '女'))
    username = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # sex = models.CharField(max_length=32, choices=gender, default='男')
    has_confirmed = models.BooleanField(default=False)
    image = models.CharField(max_length=128, default="{% static 'blog/img/default.png' %}")

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['-created_at']
        verbose_name = '用户'
        verbose_name_plural = '用户'


class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ': ' + self.code

    class Meta:
        ordering = ['-created_at']
        verbose_name = '确认码'
        verbose_name_plural = '确认码'


class Blog(models.Model):
    name = models.CharField(max_length=128)
    digest = models.TextField(max_length=500)
    content = models.TextField()
    readers = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ': ' + self.name

    class Meta:
        ordering = ['-created_at']
        verbose_name = '博客'
        verbose_name_plural = '博客'


class Comment(models.Model):
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '用户：' + self.user.username + '文章：' + self.blog.name + '评论：' + self.content

    class Meta:
        ordering = ['-created_at']
        verbose_name = '评论'
        verbose_name_plural = '评论'

