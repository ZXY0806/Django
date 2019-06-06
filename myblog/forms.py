from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(label='名字:', max_length=128, widget=forms.TextInput)
    email = forms.CharField(label='电子邮件:', max_length=128, widget=forms.EmailInput)
    password = forms.CharField(label='输入口令:', max_length=256, widget=forms.PasswordInput)
    password2 = forms.CharField(label='重复口令:', max_length=256, widget=forms.PasswordInput)


