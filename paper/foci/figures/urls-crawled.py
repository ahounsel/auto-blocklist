import sys
import sqlite3
import matplotlib
from matplotlib import pyplot
sys.path.append('/Users/ahounsel/git/censor-search/src/')
from results import *

def get_data(db, allDomains):
    data = []
    for maxRows in range(0, 1100000, 100000):
        count = len(get_results(db, maxRows, allDomains))
        data.append(count)
    return data


def make_fig():
    x = [100000*i for i in range(0, 11)]
    bigrams_all = get_data('bigrams.db', True)
    trigrams_all = get_data('trigrams.db', True)
    bigrams_subset = get_data('bigrams.db', False)
    trigrams_subset = get_data('trigrams.db', False)
    pyplot.plot(x, bigrams_all, label='Bigram results')
    pyplot.plot(x, trigrams_all, label='Trigram results')
    pyplot.plot(x, bigrams_subset, label='Bigram results w/o Top 1000')
    pyplot.plot(x, trigrams_subset, label='Trigram results w/o Top 1000')
    pyplot.xlabel('URLs crawled')
    pyplot.ylabel('Censored domains')
    pyplot.legend(loc='lower right', prop={'size': 10})
    pyplot.savefig('urls-crawled.png')
    

if __name__ == "__main__":
    make_fig()
