import webbrowser
import os
import re

#
# TODO: Clean up code by seperating the html into its own file.
# TODO: Create a function to parse html from file.
# TODO: Create a method to easily add new movies to the file.
# TODO: Create an actors arry instance variable for Movie class.
# TODO: Make the html website look better.

#Read the html components from files
def readFile(s):
    s = s + '.html'
    try:
        f = open(s,'r')
        return f.read()
    except IOError:
        print("Error: File does not exist.")
    finally:
        f.close()
        
# Styles and scripting for the page
#f = open('head.html', 'r')
#print(f.read())
main_page_head = readFile('html/head')
#print(main_page_head)


# The main page layout and title bar
main_page_content = readFile('html/main_content')
#print(main_page_content)


# A single movie entry html template
movie_tile_content = readFile('html/movie_div')
#print(movie_tile_content)


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
            trailer_youtube_id=trailer_youtube_id
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

        
toy_story = Movie("Toy Story",
                        "A story of a boy and his toys that come to life",
                        "http://upload.wikimedia.org/wikipedia/en/1/13/Toy_Story.jpg",
                        "https://www.youtube.com/watch?v=vwyZH85NQC4")

avatar = Movie("Avatar",
                     "A marine on an alien planet",
                     "http://upload.wikimedia.org/wikipedia/id/b/b0/Avatar-Teaser-Poster.jpg",
                     "https://www.youtube.com/watch?v=5PSNL1qE6VY")

big_lebowski = Movie("The Big Lebowski",
                           "The Dude is tasked to negotiate with kidnappers",
                           "https://upload.wikimedia.org/wikipedia/en/3/35/Biglebowskiposter.jpg",
                           "https://www.youtube.com/watch?v=cd-go0oBF4Y")

school_of_rock = Movie("School of Rock", "Storyline",
                             "http://upload.wikimedia.org/wikipedia/en/1/11/School_of_Rock_Poster.jpg",
                             "https://www.youtube.com/watch?v=3PsUJFEBC74")

midnight_in_paris = Movie("Midnight in Paris", "Storyline",
                                "http://upload.wikimedia.org/wikipedia/en/9/9f/Midnight_in_Paris_Poster.jpg",
                                "httpsL//www.youtube.com/watch?v=atLg2wQQxvU")

hunger_games = Movie("Hunger Games", "Storyline",
                           "http://upload.wikimedia.org/wikipedia/en/4/42/HungerGamesPoster.jpg",
                           "https://wwww.youtube.com/watch?v=PbA63a7H0bo")

movies = [toy_story, avatar, big_lebowski, school_of_rock, midnight_in_paris, hunger_games]

open_movies_page(movies)

    

