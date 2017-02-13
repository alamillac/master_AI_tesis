from pandas import read_csv, DataFrame
import numpy as np
import random


class DatasetGenerator(object):
    def __init__(self, filenameDataset, seed=None):
        print "Reading file: %s" % filenameDataset
        self.data = read_csv(filenameDataset)
        if seed:
            random.seed(seed)

    def getOptimusDataset(self, best_users=1000, best_movies=1000):
        # Get the (best_movies) most rated movies
        print "Filtering %d most rated movies" % best_movies
        size_most_rated_movies = self.data.groupby('movieId').size().sort_values(ascending=False).head(best_movies)
        most_rated_movies = size_most_rated_movies.index.values

        # Get all the ratings of (best_users) most rated movies
        print "Getting ratings of %d most rated movies" % best_movies
        ratings = self.data[self.data.movieId.isin(most_rated_movies)]

        # Get the (best_users) users with more rated top (best_movies) movies
        print "Getting %d users with more rated movies" % best_users
        size_users_with_more_ratings = ratings.groupby('userId').size().sort_values(ascending=False).head(best_users)
        users_with_more_ratings = size_users_with_more_ratings.index.values

        # Finally get the final ratings
        print "Getting output ratings"
        ratings = self.data[self.data.movieId.isin(most_rated_movies) & self.data.userId.isin(users_with_more_ratings)]
        return ratings

    def getOptimusDatasetPercentage(self, percentage=0.6):
        def n_samples(samples):
            return int(len(samples) * percentage)

        if percentage <= 0:
            return None

        if percentage >= 1:
            return self.data

        num_users = n_samples(self.data.userId.unique())
        num_movies = n_samples(self.data.movieId.unique())
        return self.getOptimusDataset(best_users=num_users, best_movies=num_movies)

    def getDataset(self, percentage=1):
        def n_samples(samples):
            return int(len(samples) * percentage)

        if percentage <= 0:
            return None

        if percentage >= 1:
            return self.data

        user_ids = self.data.userId.unique()
        movie_ids = self.data.movieId.unique()
        sample_user_ids = random.sample(user_ids, n_samples(user_ids))
        sample_movie_ids = random.sample(movie_ids, n_samples(movie_ids))
        ratings = self.data[self.data.movieId.isin(sample_movie_ids) & self.data.userId.isin(sample_user_ids)]
        return ratings

    def getMatrix(self, ratings):
        print "Creating matrix data"
        userIds = sorted(ratings.userId.unique())
        movieIds = sorted(ratings.movieId.unique())
        matrix = DataFrame([[np.nan] * len(movieIds) for i in xrange(len(userIds))], columns=movieIds, index=userIds)  # initialize matrix with nan values

        # Fill matrix
        i = 0
        rows = ratings.iterrows()
        percentage_10 = len(ratings) / 10
        percentage_done = 0
        for row in rows:
            userId = row[1].userId
            movieId = row[1].movieId
            rating = row[1].rating

            matrix.ix[userId, movieId] = rating

            if i == percentage_done * percentage_10:
                print "{0:.0f}% done".format(percentage_done * 10)
                percentage_done += 1
            i += 1

        return matrix
