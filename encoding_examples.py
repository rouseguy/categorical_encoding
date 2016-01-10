import time
import pandas as pd
import numpy as np
import gc
from sklearn import cross_validation, naive_bayes, metrics, linear_model
import matplotlib.pyplot as plt
import category_encoders
from source_data.loaders import get_cars_data, get_mushroom_data, get_splice_data
plt.style.use('ggplot')

__author__ = 'willmcginnis'


def score_models(clf, X, y, encoder, runs=100):
    """
    Takes in a classifier that supports multiclass classification, and X and a y, and returns a cross validation score.

    :param clf:
    :param X:
    :param y:
    :return:
    """

    scores = []

    for _ in range(runs):
        scores.append(cross_validation.cross_val_score(clf, encoder(X), y, n_jobs=-1, cv=5))
        gc.collect()

    scores = [y for z in [x for x in scores] for y in z]

    return float(np.mean(scores)), float(np.std(scores)), scores, encoder(X).shape[1]


def main(loader, name):
    """
    Here we iterate through the datasets and score them with a classifier using different encodings.
    :return:
    """

    scores = []
    raw_scores_ds = {}

    # first get the dataset
    X, y, mapping = loader()
    X = category_encoders.ordinal_encoding(X)

    clf = linear_model.SGDClassifier(n_iter=500)

    # try each encoding method available
    for encoder_name in category_encoders.__all__:
        encoder = category_encoders.__dict__[encoder_name]
        start_time = time.time()
        score, stds, raw_scores, dim = score_models(clf, X, y, encoder)
        scores.append([encoder_name, name, dim, score, stds, time.time() - start_time])
        raw_scores_ds[encoder_name] = raw_scores
        gc.collect()

    results = pd.DataFrame(scores, columns=['Encoding', 'Dataset', 'Dimensionality', 'Avg. Score', 'Score StDev', 'Elapsed Time'])

    raw = pd.DataFrame.from_dict(raw_scores_ds)
    ax = raw.plot(kind='box', return_type='axes')
    plt.title('Scores for Encodings on %s Dataset' % (name, ))
    plt.ylabel('Score (higher better)')
    for tick in ax.get_xticklabels():
        tick.set_rotation(90)
    plt.grid()
    plt.tight_layout()
    plt.show()

    return results, raw

if __name__ == '__main__':
    out, raw = main(get_mushroom_data, 'Mushroom')
    print(out.sort_values(by=['Dataset', 'Avg. Score']))
    #
    # out, raw = main(get_cars_data, 'Cars')
    # print(out.sort_values(by=['Dataset', 'Avg. Score']))

    # out, raw = main(get_splice_data, 'Splice')
    # print(out.sort_values(by=['Dataset', 'Avg. Score']))
