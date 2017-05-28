#!/usr/bin/env python

import json
from os import path
from datasetGenerator import DatasetGenerator
from concensusFn import least_misery, mean, multiplicative, most_pleasure
import logging
import matplotlib.pyplot as plt
import numpy as np

import sys
import signal

CURRENT_DIR = path.dirname(path.abspath(__file__))
DIR_CACHE_MODELS = path.join(CURRENT_DIR, 'cache')

logging.basicConfig()

logger = logging.getLogger('build_min_data')
logger.setLevel(logging.DEBUG)

# Signal handler
def exit(signum, frame):
    sig_name = tuple(v for v, k in signal.__dict__.items() if k == signum)[0]
    logger.warn('Received signal %s', sig_name)
    sys.exit(0)

for s in [signal.SIGINT, signal.SIGTERM, signal.SIGABRT]:
    signal.signal(s, exit)


CURRENT_DIR = path.dirname(path.abspath(__file__))
DATA_DIR = path.join(CURRENT_DIR, '..', 'data')

dataFilename = path.join(DATA_DIR, 'ratings.csv')

logger.debug("Opening database %s" % dataFilename)
generator = DatasetGenerator(dataFilename, seed=1985)

# Filter dataset. (Remove users with less than 20 ratings)
logger.debug("Filter dataset")
ratings = generator.filterDataset()

# Generating groups of users
def get_groups(generator, ratings):
    groups_cache_file = path.join(DIR_CACHE_MODELS, 'groups.json')
    # Read grops from cache
    try:
        with open(groups_cache_file) as f:
            groups = json.load(f)

        logger.debug("Groups read from cache")
        return groups
    except:
        pass

    group_sizes = [
        (50, 2),
        (18, 3),
        (16, 4),
        (7, 5),
        (5, 6),
        (4, 7)
    ]
    groups = []
    for num_groups, size in group_sizes:
        logger.debug("Generating %d groups of %d users", num_groups, size)
        for group, group_type in generator.getGroupUsers(ratings, num_groups, size):
            logger.debug("Group generated: %s -> %d", group_type, len(group))
            groups.append((group.tolist(), group_type))

    # Save groups in cache
    logger.debug("Saving groups in cache")
    try:
        with open(groups_cache_file, 'w') as f:
            json.dump(groups, f, indent=4)
    except:
        logger.debug("Groups couldn't be saved in cache")

    logger.debug("Groups saved in %s", groups_cache_file)
    return groups

groups = get_groups(generator, ratings)

# Evaluate concensus algorithms
results = []
concensus_alg = [{
    "name": "Least misery",
    "fn": least_misery
}, {
    "name": "Mean",
    "fn": mean
}, {
    "name": "Multiplicative",
    "fn": multiplicative
}, {
    "name": "Most pleasure",
    "fn": most_pleasure
}]
group_sizes = set()
for group, group_type in groups:
    for concensus_fn_name, evaluation_success, evaluation_unsuccess in generator.evaluateConcensusFns(ratings, group, concensus_alg):
        # TODO show number of co-rated movies
        logger.debug("Group_size: %d, Group_type: %s, Concensus_alg: %s, Success: %.2f%%, Unsuccess: %.2f%%", len(group), group_type, concensus_fn_name, evaluation_success, evaluation_unsuccess)
        group_sizes.add(len(group))
        results.append({
            "concensus_name": concensus_fn_name,
            "success_value": evaluation_success,
            "unsuccess_value": evaluation_unsuccess,
            "group_type": group_type,
            "group_size": len(group)
        })


# Process results
def filter_results(results, value_type, group_size, concensus_name, group_type):
    return [result[value_type] for result in results if result['group_size'] == group_size and result['concensus_name'] == concensus_name and result['group_type'] == group_type]

def mean_and_std(values):
    return np.mean(values), np.std(values)

import ipdb; ipdb.set_trace()  # BREAKPOINT
graphs = []
for value_type in ["success_value", "unsuccess_value"]:
    for group_size in group_sizes:
        # Filter success values with group_size
        graph_info = []
        for concensus in concensus_alg:
            means_values = []
            std_values = []
            for group_type in ["similar", "random", "disimilar"]:
                mean_result, std_result = mean_and_std(filter_results(results, value_type, group_size, concensus['name'], group_type))
                means_values.append(mean_result)
                std_values.append(std_result)

            graph_info.append({
                'label': concensus['name'],
                'means': means_values,
                'std': std_values
            })
        graphs.append({
            'data': graph_info,
            'group_size': group_size,
            'value_type': "Success" if value_type == "success_value" else "Unsuccess"
        })


# Plot results
full_bar_width = 0.7
bar_width = full_bar_width / len(concensus_alg)
opacity = 0.4
error_config = {'ecolor': '0.3'}

for graph in graphs:
    logger.debug("Show graph: %s group %d", graph['value_type'], graph['group_size'])
    i = 0
    for plot in graph['data']:
        index = np.arange(len(plot['means'])) #similar, random and disimilar
        plt.bar(index + (i * bar_width), plot['means'], bar_width, alpha=opacity, yerr=plot['std'], error_kw=error_config, label=plot['label'])
        i += 1

    plt.xlabel('Groups')
    plt.ylabel(graph['value_type'])
    plt.title('%s group %d' % (graph['value_type'], graph['group_size']))
    plt.xticks(index + (bar_width * len(concensus_alg) / 2), ('Similar', 'Random', 'Disimilar'))
    plt.legend()
    plt.tight_layout()
    plt.show()


sys.exit(0)

#bins = np.linspace(0, 2500, 100)
#plt.hist(stats_100['countRatingsByUsers'], bins, normed=1, alpha=0.5)
#plt.hist(stats_opt_40['countRatingsByUsers'], bins, normed=1, alpha=0.5)
#plt.hist(stats_opt['countRatingsByUsers'], bins, normed=1, alpha=0.5)
#plt.title("Histogram user ratings")
#plt.show()


# Save it
#rating_min_filename = path.join(DATA_DIR, 'ratings_min.csv')
#logger.debug("Saving file to %s" % rating_min_filename)
#ratings.to_csv(rating_min_filename, index=False)

# Save matrix data
#logger.debug("Generating matrix")
#matrix = generator.getMatrix(ratings)
#matrix_filename = path.join(DATA_DIR, 'matrix.csv')
#logger.debug("Saving matrix file to %s" % matrix_filename)
#matrix.to_csv(matrix_filename)
