from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('pinpoint-challenge/', views.pinpoint_challenge, name='pinpoint_challenge'),
    path('pinpoint-challenge/play/', views.pinpoint_challenge_play, name='pinpoint_challenge_play'),
    path('add-trivia-category/', views.add_trivia_category, name='add_trivia_category'),
    path('edit-trivia-category/<int:category_id>/', views.edit_trivia_category, name='edit_trivia_category'),
    path('delete-trivia-category/<int:category_id>/', views.delete_trivia_category, name='delete_trivia_category'),
    path('categories-and-players/', views.categories_and_players, name='categories_and_players'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]