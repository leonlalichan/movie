from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.db.models import Avg
from .models import UserProfile, Movie, Genre, Review
from sqlite3 import IntegrityError
from django.contrib import messages
from django.core.paginator import Paginator,EmptyPage, InvalidPage


def home(request):
    return render(request, 'base.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already exists'})

        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            UserProfile.objects.create(user=user, first_name=first_name, last_name=last_name, email=email)

            messages.success(request, 'User created successfully')  # Add this line
            return redirect('login')
        except IntegrityError:
            return render(request, 'register.html', {'error': 'An error occurred. Please try again.'})

    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome,{user.username}')
            return redirect('profile')
        else:
            return HttpResponse('Invalid login credentials')
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('/')

@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'profile.html', {'user_profile': user_profile})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.first_name = request.POST['first_name']
        user_profile.last_name = request.POST['last_name']
        user_profile.email = request.POST['email']
        user_profile.bio = request.POST['bio']
        user_profile.save()
        return redirect('profile')
    return render(request, 'edit_profile.html')

@login_required
def add_movie(request):
    if request.method == 'POST':
        title = request.POST['title']
        poster = request.FILES['poster']
        description = request.POST['description']
        release_date = request.POST['release_date']
        actors = request.POST['actors']
        genre_id = request.POST['genre']
        youtube_trailer = request.POST['youtube_trailer']

        genre = get_object_or_404(Genre, id=genre_id)

        Movie.objects.create(
            title=title,
            poster=poster,
            description=description,
            release_date=release_date,
            actors=actors,
            genre=genre,
            youtube_trailer=youtube_trailer,
            user=request.user
        )
        return redirect('movies')

    genres = Genre.objects.all()
    return render(request, 'add_movie.html', {'genres': genres})


@login_required
def edit_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.user != movie.user:
        return HttpResponse('You are not allowed to edit this movie')

    if request.method == 'POST':
        movie.title = request.POST['title']
        if 'poster' in request.FILES:
            movie.poster = request.FILES['poster']
        movie.description = request.POST['description']
        movie.release_date = request.POST['release_date']
        movie.actors = request.POST['actors']
        genre_id = request.POST['genre']
        genre = get_object_or_404(Genre, id=genre_id)
        movie.genre = genre
        movie.youtube_trailer = request.POST['youtube_trailer']
        movie.save()
        return redirect('movies')

    genres = Genre.objects.all()
    return render(request, 'edit_movie.html', {'movie': movie, 'genres': genres})


@login_required
def delete_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.user == movie.user:
        movie.delete()
        return redirect('movies')
    else:
        return HttpResponse('You are not allowed to delete this movie')

def movies(request):
    query = request.GET.get('query', '')
    selected_genre_id = request.GET.get('genre', '')

    if query:
        movies_list = Movie.objects.filter(title__icontains=query)
    else:
        movies_list = Movie.objects.all()

    if selected_genre_id:
        movies_list = movies_list.filter(genre_id=selected_genre_id)

    paginator = Paginator(movies_list, 6)  # Show 6 movies per page

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        movies = paginator.page(page)
    except (EmptyPage, InvalidPage):
        movies = paginator.page(paginator.num_pages)

    genres = Genre.objects.all()

    context = {
        'movies': movies,
        'genres': genres,
        'selected_genre_id': selected_genre_id,
        'query': query,
    }
    return render(request, 'movies.html', context)

def search_movies(request):
    if 'query' in request.GET:
        query = request.GET['query']
        found_movies = Movie.objects.filter(title__icontains=query)
    else:
        found_movies = Movie.objects.all()
    return render(request, 'movies.html', {'movies': found_movies})

@login_required
def add_review(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')
        Review.objects.create(user=request.user, movie=movie, rating=rating, comment=comment)
        return redirect('movie_detail', movie_id=movie.id)
    return render(request, 'add_review.html', {'movie': movie})

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    reviews = Review.objects.filter(movie=movie)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    context = {
        'movie': movie,
        'reviews': reviews,
        'average_rating': average_rating,
    }
    return render(request, 'movie_detail.html', context)

def movie_list(request):
    genres = Genre.objects.all()
    selected_genre = request.GET.get('genre')
    if selected_genre:
        filtered_movies = Movie.objects.filter(genre__name=selected_genre)
    else:
        filtered_movies = Movie.objects.all()
    return render(request, 'movies.html', {'movies': filtered_movies, 'genres': genres, 'selected_genre': selected_genre})


def add_genre(request):
    if request.method == 'POST':
        name = request.POST['name']
        Genre.objects.create(name=name)
        return redirect('movies')  # Redirect to the movies list or any other relevant page
    return render(request, 'add_genre.html')