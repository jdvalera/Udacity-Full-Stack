import webbrowser
import os
import re
import csv


#Read the html components from files and return it as a string
def readFile(s):
    s = s + '.html'
    try:
        f = open(s,'r')
        return f.read()
    except IOError:
        print("Error: File does not exist.")
    finally:
        f.close()
        

def create_movie_tiles_content(movies):
    # The HTML content for this section of the page
    content = ''
    for movie in movies:
        # Extract the youtube ID from the url
        youtube_id_match = re.search(
            r'(?<=v=)[^&#]+', movie.trailer_youtube_url)
        youtube_id_match = youtube_id_match or re.search(
            r'(?<=be/)[^&#]+', movie.trailer_youtube_url)
        trailer_youtube_id = (youtube_id_match.group(0) if youtube_id_match
                              else None)

        # Append the tile for the movie with its content filled in
        content += movie_tile_content.format(
            movie_title=movie.title,
            poster_image_url=movie.poster_image_url,
            trailer_youtube_id=trailer_youtube_id,
            movie_storyline=movie.storyline,
            actors = movie.movie_actors,
            directors = movie.directed_by,
            rating = movie.movie_rating,
            year = movie.release_year
        )
    return content


def open_movies_page(movies):
    # Create or overwrite the output file
    output_file = open('fresh_tomatoes.html', 'w')

    # Replace the movie tiles placeholder generated content
    rendered_content = main_page_content.format(
        movie_tiles=create_movie_tiles_content(movies))

    # Output the file
    output_file.write(main_page_head + rendered_content)
    output_file.close()

    # open the output file in the browser (in a new tab, if possible)
    url = os.path.abspath(output_file.name)
    webbrowser.open('file://' + url, new=2)


class Movie():
    """ This class provides a way to store movie related information """
    
    def __init__(self, movie_title, movie_storyline, poster_image, trailer_youtube, directed_by, movie_actors, movie_rating, release_year):
        self.title = movie_title
        self.storyline = movie_storyline
        self.poster_image_url = poster_image
        self.trailer_youtube_url = trailer_youtube
        self.directed_by = directed_by
        self.movie_actors = movie_actors
        self.movie_rating = movie_rating
        self.release_year = release_year

    def show_trailer(self):
        webbrowser.open(self.trailer_youtube_url)


#Read movie info from a CSV file and create an instance of Movie for each movie on the list. Append each instance to an array.
def createMovies():
    movies = []
    file = open('movie_list.csv')
    reader = csv.reader(file)
    data = list(reader)
    for i in range(1, len(data)):
        movies.append(Movie(data[i][0],data[i][1],data[i][2],data[i][3],data[i][4],data[i][5],data[i][6],data[i][7]))
    return movies

# Read html header w/ CSS and Scripts for page
main_page_head = readFile('html/head')


# The main page layout
main_page_content = readFile('html/main_content')


# A single movie entry html template
movie_tile_content = readFile('html/movie_div')


movies = createMovies()

open_movies_page(movies)

    

