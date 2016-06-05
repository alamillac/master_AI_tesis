#!/usr/bin/env python

from pandas import read_csv, DataFrame
import numpy as np
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

# Save matrix data
print "Creating matrix data"
userIds = sorted(ratings.userId.unique())
movieIds = sorted(ratings.movieId.unique())
matrix = DataFrame([[np.nan] * len(userIds) for i in xrange(len(movieIds))], columns=userIds, index=movieIds)  # initialize matrix with nan values

# Fill matrix
i = 0
rows = ratings.iterrows()
percentage_10 = len(ratings) / 10
percentage_done = 0
for row in rows:
    userId = row[1].userId
    movieId = row[1].movieId
    rating = row[1].rating

    matrix.ix[movieId, userId] = rating

    if i == percentage_done * percentage_10:
        print "{0:.0f}% done".format(percentage_done * 10)
        percentage_done += 1
    i += 1

matrix_filename = path.join(DATA_DIR, 'matrix.csv')
print "Saving matrix file to %s" % matrix_filename
matrix.to_csv(matrix_filename)
