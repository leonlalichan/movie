# movie_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('movies/<int:movie_id>/review/', views.add_review, name='add_review'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movies/<int:movie_id>/edit/', views.edit_movie, name='edit_movie'),
    path('movies/<int:movie_id>/delete/', views.delete_movie, name='delete_movie'),
    path('movies/add/', views.add_movie, name='add_movie'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('add_movie/', views.add_movie, name='add_movie'),
    path('edit_movie/<int:movie_id>/', views.edit_movie, name='edit_movie'),
    path('delete_movie/<int:movie_id>/', views.delete_movie, name='delete_movie'),
    path('', views.movies, name='movies'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('search/', views.search_movies, name='search_movies'),
    path('add_genre/', views.add_genre, name='add_genre'),
]
