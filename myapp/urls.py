from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('second_page/', views.second_page, name='second_page'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]