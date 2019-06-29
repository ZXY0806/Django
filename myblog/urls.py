from django.urls import path
from . import views

# app_name = 'myblog'
urlpatterns = [
    path('', views.index, name='index'),
    path('<str:username>/blogs/<int:blog_id>/', views.Blog.as_view(), name='blog'),
    path('<str:username>/blogs/<int:blog_id>/comment/', views.Comment.as_view(), name='comment'),
    path('hot/', views.hot, name='hot'),
    path('following/', views.following, name='following'),
    path('mycommented/', views.mycommented, name='mycommented'),
    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('confirm/', views.confirm, name='confirm'),

]

