from unicodedata import name
from django.urls import path
from django.views import View
from .views import PostListView, PostDetailedView, PostCreateView, PostUpdateView, PostDeleteView, SearchResultsView
from . import views

urlpatterns=[
    path('',PostListView.as_view(),name='home'),
    path('post/<int:pk>/',PostDetailedView.as_view(),name='post-detail'),
    path('post/new/',PostCreateView.as_view(),name='post-create'),
    path('post/<int:pk>/update',PostUpdateView.as_view(),name='post-update'),
    path('post/<int:pk>/delete',PostDeleteView.as_view(),name='post-delete'),
    path('search/',SearchResultsView.as_view(),name='search'),
    path('post/<int:pk>/favourite_post',views.favourite_post,name='favourite_post'),
    path('about/',views.about,name='about'),
    path('register/', views.register_request, name="register"),
    path('register_organizer/', views.register_organizer, name="register_organizer"),
    path("login/", views.login_request, name="login"),
    path("login_organizer/", views.login_organizer, name="login_organizer"),
    path("login_admin/", views.login_admin, name="login_admin"),
    path("logout", views.logout_request, name= "logout"),
    path('users/',views.list_users,name='users'),
    path('fav_posts/',views.post_favourites,name='post_favourites'),
    path('my_events/',views.my_events,name='my_events'),
    path('<str:username>/del_user/',views.del_user,name='delete_user')
]