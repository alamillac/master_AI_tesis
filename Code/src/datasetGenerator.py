from pandas import read_csv, DataFrame, Series
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

    def getOptimumDataset(self, best_users=1000, best_movies=1000):
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

    def getOptimumDatasetPercentage(self, percentage=0.6):
        def n_samples(samples):
            return int(len(samples) * percentage)

        if percentage <= 0:
            return None

        if percentage >= 1:
            return self.data

        num_users = n_samples(self.data.userId.unique())
        num_movies = n_samples(self.data.movieId.unique())
        return self.getOptimumDataset(best_users=num_users, best_movies=num_movies)

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

    def getDataset(self, num_users, num_movies=None, more_rated_movies=None):
        user_ids = self.data.userId.unique()
        sample_user_ids = random.sample(user_ids, num_users)

        # get movies rated by sample_users
        ratings_of_sample_users = self.data[self.data.userId.isin(sample_user_ids)]
        if not num_movies:
            return ratings_of_sample_users

        movie_ids = ratings_of_sample_users.movieId.unique()
        if num_movies >= len(movie_ids):
            logger.warning("There is not enough movies. Returning %d movies", len(movie_ids))
            return ratings_of_sample_users

        if more_rated_movies:
            # More rated movies samples
            size_most_rated_movies = ratings_of_sample_users.groupby('movieId').size().sort_values(ascending=False).head(num_movies)
            sample_movie_ids = size_most_rated_movies.index.values
        else:
            # Random movie samples
            sample_movie_ids = random.sample(movie_ids, num_movies)

        ratings = ratings_of_sample_users[ratings_of_sample_users.movieId.isin(sample_movie_ids)]
        return ratings

    def getMostSimilarUsers(self, ratings, user_id, num_users):
        """
        Get the $num_users most similars to $user_id in $ratings dataset
        """
        distances = self.getDistances(ratings, user_id)
        similar_users = distances.sort_values().head(num_users).index
        remaining_dataset = ratings[~ratings.userId.isin(similar_users)]
        return similar_users, remaining_dataset

    def getMostDisimilarUsers(self, ratings, user_id, num_users):
        """
        Get the $num_users most disimilars to $user_id in $ratings dataset
        """
        distances = self.getDistances(ratings, user_id)
        disimilar_users = distances.sort_values(ascending=False).head(num_users).index
        remaining_dataset = ratings[~ratings.userId.isin(disimilar_users)]
        return disimilar_users, remaining_dataset

    def getRandomUsers(self, ratings, num_users):
        user_ids = ratings.userId.unique()
        if len(user_ids) <= num_users:
            sample_user_ids = user_ids
        else:
            sample_user_ids = random.sample(user_ids, num_users)
        remaining_dataset = ratings[~ratings.userId.isin(sample_user_ids)]
        return sample_user_ids, remaining_dataset

    def getGroupUsers(self, ratings, groups):
        def selectSimilarGroup(ratings, groups):
            user_ids = ratings.userId.unique()
            user_id = random.choice(user_ids)
            num_users = random.choice(groups)
            return self.getMostSimilarUsers(ratings, user_id, num_users)

        def selectDisimilarGroup(ratings, groups):
            user_ids = ratings.userId.unique()
            user_id = random.choice(user_ids)
            num_users = random.choice(groups)
            return self.getMostDisimilarUsers(ratings, user_id, num_users)

        def selectRandomGroup(ratings, groups):
            num_users = random.choice(groups)
            return self.getRandomUsers(ratings, num_users)

        selectFunctions = [selectSimilarGroup, selectDisimilarGroup, selectRandomGroup]

        remaining_dataset = ratings
        generated_groups = []
        while not remaining_dataset.empty:
            selectFunction = random.choice(selectFunctions)
            user_groups, remaining_dataset = selectFunction(remaining_dataset, groups)
            generated_groups.append(user_groups)

        return generated_groups

    def getDistances(self, ratings, user_id):
        matrix = self.getMatrix(ratings)
        distances = []
        users = []
        num_rated_movies = matrix.loc[user_id].count()
        for user_idx in matrix.index:
            common_rated_movies = np.count_nonzero(~(matrix.loc[user_idx].isnull() | matrix.loc[user_id].isnull()))
            if common_rated_movies:
                distance = abs(matrix.loc[user_idx] - matrix.loc[user_id]).sum()
                normalized_distance = distance * num_rated_movies / common_rated_movies
            else:
                normalized_distance = np.nan
            # Save distance between user_idx and user_id
            distances.append(normalized_distance)
            users.append(user_idx)
        return Series(distances, index=users)

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
