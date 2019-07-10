from django.urls import path
from . import views

# app_name = 'myblog'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('register/', views.Register.as_view(), name='register'),
    path('logout/', views.logout, name='logout'),
    path('confirm/', views.confirm, name='confirm'),
    path('u/<str:username>/', views.MyBlog.as_view(), name='myblog'),
    path('u/<str:username>/blogs/<int:blog_id>/', views.Blog.as_view(), name='blog'),
    path('u/<str:username>/blogs/<int:blog_id>/comment/', views.Comment.as_view(), name='comment'),
    path('resume/<str:username>/', views.Resume.as_view(), name='resume'),
    path('hot/', views.hot, name='hot'),
    path('following/', views.following, name='following'),
    path('mycommented/', views.mycommented, name='mycommented'),


]

