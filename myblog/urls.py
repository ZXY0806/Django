from django.urls import path
from . import views

# app_name = 'myblog'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

]

