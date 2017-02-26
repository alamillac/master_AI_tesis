from pandas import read_csv, DataFrame
import numpy as np
import random
import logging

logger = logging.getLogger('datasetGenerator')


class DatasetGenerator(object):
    def __init__(self, filenameDataset, seed=None):
        logger.debug("Reading file: %s" % filenameDataset)
        self.data = read_csv(filenameDataset)
        if seed:
            random.seed(seed)

    def getOptimusDataset(self, best_users=1000, best_movies=1000):
        # Get the (best_movies) most rated movies
        logger.debug("Filtering %d most rated movies" % best_movies)
        size_most_rated_movies = self.data.groupby('movieId').size().sort_values(ascending=False).head(best_movies)
        most_rated_movies = size_most_rated_movies.index.values

        # Get all the ratings of (best_users) most rated movies
        logger.debug("Getting ratings of %d most rated movies" % best_movies)
        ratings = self.data[self.data.movieId.isin(most_rated_movies)]

        # Get the (best_users) users with more rated top (best_movies) movies
        logger.debug("Getting %d users with more rated movies" % best_users)
        size_users_with_more_ratings = ratings.groupby('userId').size().sort_values(ascending=False).head(best_users)
        users_with_more_ratings = size_users_with_more_ratings.index.values

        # Finally get the final ratings
        logger.debug("Getting output ratings")
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

    def getDatasetPercentage(self, percentage=1):
        def n_samples(samples):
            return int(len(samples) * percentage)

        if percentage <= 0:
            return None

        if percentage >= 1:
            return self.data

        user_ids = self.data.userId.unique()
        movie_ids = self.data.movieId.unique()

        return self.getDataset(n_samples(user_ids), n_samples(movie_ids))

    def getDataset(self, num_users, num_movies):
        user_ids = self.data.userId.unique()
        movie_ids = self.data.movieId.unique()
        sample_user_ids = random.sample(user_ids, num_users)
        sample_movie_ids = random.sample(movie_ids, num_movies)
        ratings = self.data[self.data.movieId.isin(sample_movie_ids) & self.data.userId.isin(sample_user_ids)]
        return ratings

    def getMatrix(self, ratings):
        logger.debug("Creating matrix data")
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
                logger.debug("{0:.0f}% done".format(percentage_done * 10))
                percentage_done += 1
            i += 1

        return matrix

    def getStatsFromDataset(self, dataset):
        num_users = len(dataset.userId.unique())
        num_movies = len(dataset.movieId.unique())
        count_ratings_by_users = dataset.groupby('userId')['rating'].count()
        count_ratings_by_movies = dataset.groupby('movieId')['rating'].count()
        return {
            "numUsers": num_users,
            "numMovies": num_movies,
            "numRatings": len(dataset),
            "meanRatingsByUsers": count_ratings_by_users.mean(),
            "meanRatingsByMovies": count_ratings_by_movies.mean(),
            "standardDeviationRatingsByUsers": count_ratings_by_users.std(),
            "standardDeviationRatingsByMovies": count_ratings_by_movies.std(),
            "countRatingsByUsers": count_ratings_by_users,
            "countRatingsByMovies": count_ratings_by_movies,
            "histRatingsByUsers": np.histogram(count_ratings_by_users),
            "histRatingsByMovies": np.histogram(count_ratings_by_movies)
        }
