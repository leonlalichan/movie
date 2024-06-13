from django.contrib import admin

# Register your models here.
# movie_app/admin.py

from django.contrib import admin
from .models import UserProfile, Movie,Genre

admin.site.register(UserProfile)
admin.site.register(Movie)
admin.site.register(Genre)