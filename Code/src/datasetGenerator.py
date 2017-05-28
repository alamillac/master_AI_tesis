from pandas import read_csv, DataFrame, Series
from errors import InvalidGroupError, MaxInvalidIterationsError
import numpy as np
import random
import logging

logger = logging.getLogger('datasetGenerator')
logger.setLevel(logging.DEBUG)


class DatasetGenerator(object):
    def __init__(self, filenameDataset, seed=None):
        logger.debug("Reading file: %s" % filenameDataset)
        self.data = read_csv(filenameDataset)
        if seed:
            random.seed(seed)

    def filterDataset(self, num_ratings=20):
        logger.debug("Filtering users with more than %d rated movies" % num_ratings)
        size_users = self.data.groupby('userId').size()
        valid_users = [user_id for user_id in size_users.index if size_users[user_id] >= num_ratings]
        ratings = self.data[self.data.userId.isin(valid_users)]
        return ratings

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

    def getCoRatedMovies(self, ratings, users_id):
        if len(users_id) == 0:
            return set()

        co_rated_movies = set(ratings.movieId.unique())
        for user_id in users_id:
            movies_rated_by_user = set(ratings[ratings.userId.isin([user_id])].movieId.unique())
            co_rated_movies.intersection_update(movies_rated_by_user)
        return co_rated_movies

    def getMostSimilarUsers(self, ratings, user_id, num_users):
        """
        Get the $num_users most similars to $user_id in $ratings dataset
        """
        logger.debug("Getting %d most similar users for %s", num_users, user_id)
        distances = self.getDistances(ratings, user_id)
        similar_users = distances.sort_values().head(num_users).index
        if len(self.getCoRatedMovies(ratings, similar_users)) < 10:
            raise InvalidGroupError()
        return similar_users

    def getMostDisimilarUsers(self, ratings, user_id, num_users):
        """
        Get the $num_users most disimilars to $user_id in $ratings dataset
        """
        logger.debug("Getting %d most disimilar users for %s", num_users, user_id)
        distances = self.getDistances(ratings, user_id)
        disimilar_users = distances.sort_values(ascending=False).head(num_users).index
        if len(self.getCoRatedMovies(ratings, disimilar_users)) < 10:
            raise InvalidGroupError()
        return disimilar_users

    def getRandomUsers(self, ratings, num_users):
        logger.debug("Getting %d random users", num_users)
        user_ids = ratings.userId.unique()
        if len(user_ids) <= num_users:
            sample_user_ids = user_ids
        else:
            sample_user_ids = random.sample(user_ids, num_users)

        if len(self.getCoRatedMovies(ratings, sample_user_ids)) < 10:
            raise InvalidGroupError()
        return sample_user_ids

    def getGroupUsersFn(self, ratings, num_groups, size, selectFunction):
        remaining_dataset = ratings
        num_generated_groups = 0
        num_invalid = 0
        while num_generated_groups < num_groups:
            try:
                group = selectFunction(remaining_dataset, size)
                num_invalid = 0
                num_generated_groups += 1
                remaining_dataset = remaining_dataset[~remaining_dataset.userId.isin(group)]
                yield group
            except InvalidGroupError:
                num_invalid += 1
                logger.warning("Invalid group iteration %d", num_invalid)
                if num_invalid > 20:
                    raise MaxInvalidIterationsError()

    def getGroupUsers(self, ratings, num_groups, size):
        def reduceRatings(ratings, user_id):
            # Reduce the number of ratings
            logger.debug("Reducing ratings for user %s", user_id)
            filtered_ratings = self.filterCoRatedMovies(ratings, user_id)
            size_filtered_users = filtered_ratings.groupby('userId').size().sort_values(ascending=False).head(10000)
            filtered_user_ids = size_filtered_users.index.values
            filtered_ratings = filtered_ratings[filtered_ratings.userId.isin(filtered_user_ids)]
            logger.debug("Ratings reduced from %d to %d", len(ratings), len(filtered_ratings))
            return filtered_ratings

        def selectSimilarGroup(ratings, num_users):
            user_ids = ratings.userId.unique()
            user_id = random.choice(user_ids)
            reduced_ratings = reduceRatings(ratings, user_id)
            return self.getMostSimilarUsers(reduced_ratings, user_id, num_users)

        def selectDisimilarGroup(ratings, num_users):
            user_ids = ratings.userId.unique()
            user_id = random.choice(user_ids)
            reduced_ratings = reduceRatings(ratings, user_id)
            return self.getMostDisimilarUsers(reduced_ratings, user_id, num_users)

        def selectRandomGroup(ratings, num_users):
            user_ids = ratings.userId.unique()
            user_id = random.choice(user_ids)
            reduced_ratings = reduceRatings(ratings, user_id)
            return self.getRandomUsers(reduced_ratings, num_users)

        try:
            for group in self.getGroupUsersFn(ratings, num_groups, size, selectSimilarGroup):
                yield group, 'similar'
        except:
            logger.warning("Max iteration errors")

        try:
            for group in self.getGroupUsersFn(ratings, num_groups, size, selectDisimilarGroup):
                yield group, 'disimilar'
        except:
            logger.warning("Max iteration errors")

        try:
            for group in self.getGroupUsersFn(ratings, num_groups, size, selectRandomGroup):
                yield group, 'random'
        except:
            logger.warning("Max iteration errors")

    def filterCoRatedMovies(self, ratings, user_id):
        movies_rated_by_user = ratings[ratings.userId.isin([user_id])].movieId.unique()
        return ratings[ratings.movieId.isin(movies_rated_by_user)]

    def getDistances(self, ratings, user_id):
        matrix = self.getMatrix(self.filterCoRatedMovies(ratings, user_id))
        logger.debug("Getting distances for user %s", user_id)
        distances = []
        users = []
        num_rated_movies = matrix.loc[user_id].count()
        for user_idx in matrix.index:
            common_rated_movies = np.count_nonzero(~(matrix.loc[user_idx].isnull() | matrix.loc[user_id].isnull()))
            if common_rated_movies > 5: # It should have more than 5 common rated movies to get a valid distance
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

    def evaluateConcensusFns(self, ratings, group, concensusFns, n_success=3):
        def successN(model1, model2, n):
            n_movies1_id = set(model1.sort_values(ascending=False).head(n).index)
            n_movies2_id = set(model2.sort_values(ascending=False).head(n).index)
            return 1 if len(n_movies1_id.intersection(n_movies2_id)) > 0 else 0

        def unsuccessN(model1, model2, n):
            n_movies1_id = set(model1.sort_values(ascending=False).head(n).index)
            n_movies2_id = set(model2.sort_values(ascending=False).tail(n).index)
            return 1 if len(n_movies1_id.intersection(n_movies2_id)) > 0 else 0

        def evaluate(concensusFn, group_matrix):
            concensus_model = concensusFn(group_matrix)
            success_array = []
            unsuccess_array = []
            for i in range(group_matrix.shape[0]):
                user_model = group_matrix.iloc[i]
                success_array.append(
                    successN(concensus_model, user_model, n_success)
                )
                unsuccess_array.append(
                    unsuccessN(concensus_model, user_model, n_success)
                )

            return np.mean(success_array) * 100, np.mean(unsuccess_array) * 100

        # Filter ratings to only co-rated movies by all users in group
        co_rated_movies = self.getCoRatedMovies(ratings, group)
        group_ratings = ratings[ratings.movieId.isin(co_rated_movies) & ratings.userId.isin(group)]
        group_matrix = self.getMatrix(group_ratings)
        for concensusObj in concensusFns:
            evaluation_success, evaluation_unsuccess = evaluate(concensusObj['fn'], group_matrix)
            yield concensusObj['name'], evaluation_success, evaluation_unsuccess
