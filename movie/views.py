from django.shortcuts import render
from django.http import HttpResponse
from collections import defaultdict
from django.template import Template, Context
from .models import Movie
import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64
import movie

def home(request):
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'movies': movies, 'searchTerm': searchTerm})

def about(request):
    return render(request, 'about.html')

def signup(request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email': email})

def statistics_view(request):
    matplotlib.use('Agg')
    # Obtener todas las peliculas
    all_movies = Movie.objects.all()

    # Crear un diccionario para almacenar la cantidad de peliculas por año
    movie_counts_by_year = {}
    movie_counts_by_genre = defaultdict(int)

    # Filtrar las peliculas por año y contar la cantidad de peliculas por año
    for movie in all_movies:
        year = movie.year if movie.year else 'None'
        if year in movie_counts_by_year:
            movie_counts_by_year[year] += 1
        else:
            movie_counts_by_year[year] = 1

        if movie.genre: 
            first_genre = movie.genre.split(',')[0]  
            movie_counts_by_genre[first_genre] += 1

    # Ancho de las barras
    bar_width = 0.5
    # Posiciones de las barras
    bar_positions = range(len(movie_counts_by_year))

    # Crear la gráfica de barras
    plt.bar(bar_positions, movie_counts_by_year.values(), width=bar_width, align='center')

    # Personalizar la gráfica
    plt.title( 'Movies per year')
    plt.xlabel( 'Year')
    plt.ylabel( 'Number of movies')
    plt.xticks(bar_positions, movie_counts_by_year.keys(), rotation=90)
    
    # Ajustar el espaciado entre las barras
    plt.subplots_adjust(bottom=0.3)

    # Guardar la gráfica en un objeto BytesIO
    buffer = io.BytesIO()
    plt. savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    # Convertir la gráfica a base64
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    genre = list(movie_counts_by_genre.keys())
    counts = list(movie_counts_by_genre.values())
    
    plt.bar(genre, counts)
    plt.title('Movies per genre')
    plt.xlabel('Genre')
    plt.ylabel('Number of movies')
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.3)
    
    buffer_genre = io.BytesIO()
    plt.savefig(buffer_genre, format='png')
    buffer_genre.seek(0)
    plt.close()
    
    image_png_genre = buffer_genre.getvalue()
    buffer_genre.close()
    graphic_genre = base64.b64encode(image_png_genre)
    graphic_genre = graphic_genre.decode('utf-8')
    
    # Renderizar la plantilla statistics.html con la gráfica
    return render(request, 'statistics.html', {'graphic': graphic, 'graphic_genre': graphic_genre})
    
