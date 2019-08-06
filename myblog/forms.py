from django import forms
from DjangoUeditor.models import UEditorField


class RegisterForm(forms.Form):
    username = forms.CharField(label='名字:', max_length=128, widget=forms.TextInput)
    email = forms.EmailField(label='电子邮件:', max_length=128, widget=forms.EmailInput)
    password1 = forms.CharField(label='输入口令:', max_length=256, widget=forms.PasswordInput)
    password2 = forms.CharField(label='重复口令:', max_length=256, widget=forms.PasswordInput)


class LoginForm(forms.Form):
    username = forms.CharField(label='名字:', max_length=128, widget=forms.TextInput)
    password = forms.CharField(label='输入口令:', max_length=256, widget=forms.PasswordInput)


class BlogForm(forms.Form):
    name = forms.CharField(max_length=128, label='标题', widget=forms.TextInput(attrs={'class': 'uk-width-1-1'}))
    digest = forms.CharField(max_length=500, label='摘要', widget=forms.Textarea(attrs={'class': 'uk-width-1-1'}))
    content = forms.CharField(label='内容', widget=forms.Textarea(attrs={'id': 'content', 'class': 'uk-width-1-1'}))
