#!/usr/bin/env python

from pandas import read_csv
from os import path

CURRENT_DIR = path.dirname(path.abspath(__file__))
DATA_DIR = path.join(CURRENT_DIR, '..', 'data')

dataFilename = path.join(DATA_DIR, 'ratings.csv')
print "Reading file: %s" % dataFilename
data = read_csv(dataFilename)

# Get the 1000 most rated movies
print "Filtering 1000 most rated movies"
size_most_rated_movies = data.groupby('movieId').size().sort_values(ascending=False).head(1000)
most_rated_movies = size_most_rated_movies.index.values

# Get all the ratings of 1000 most rated movies
print "Getting ratings of 1000 most rated movies"
ratings = data[data.movieId.isin(most_rated_movies)]

# Get the 1000 users with more rated top 1000 movies
print "Getting 1000 users with more rated movies"
size_users_with_more_ratings = ratings.groupby('userId').size().sort_values(ascending=False).head(1000)
users_with_more_ratings = size_users_with_more_ratings.index.values

# Finally get the final ratings
print "Getting output ratings"
ratings = data[data.movieId.isin(most_rated_movies) & data.userId.isin(users_with_more_ratings)]

# Save it
rating_min_filename = path.join(DATA_DIR, 'ratings_min.csv')
print "Saving file to %s" % rating_min_filename
ratings.to_csv(rating_min_filename, index=False)
