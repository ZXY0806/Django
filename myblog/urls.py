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
    path('u/<str:username>/upload_photo', views.UploadPhoto.as_view(), name='upload_photo'),
    path('u/<str:username>/account_set', views.AccountSet.as_view(), name='account_set'),
    path('edit/blog', views.EditBlog.as_view(), name='edit_blog'),
    path('delete/blog', views.DeleteBlog.as_view(), name='delete_blog'),
    path('manage/blogs', views.ManageBlogs.as_view(), name='manage_blogs'),
    path('u/<str:username>/blogs/<int:blog_id>/comment/', views.Comment.as_view(), name='comment'),
    path('resume/<str:username>/', views.Resume.as_view(), name='resume'),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('unfollow/<str:username>/', views.unfollow, name='unfollow'),
    path('hot/', views.hot, name='hot'),
    path('following/', views.following, name='following'),
    path('mycommented/', views.mycommented, name='mycommented'),

]

