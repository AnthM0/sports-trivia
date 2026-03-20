from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('pinpoint-challenge/', views.pinpoint_challenge, name='pinpoint_challenge'),
    path('add-trivia-category/', views.add_trivia_category, name='add_trivia_category'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]