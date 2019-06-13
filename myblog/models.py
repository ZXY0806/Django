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
    image = models.CharField(max_length=128, default="static 'blog/img/default.png'")

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


