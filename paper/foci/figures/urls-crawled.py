import sys
import sqlite3
import matplotlib
from matplotlib import pyplot
sys.path.append('../../../src/')
from results import *

def get_data(db):
    data = []
    for maxRows in range(0, 1100000, 100000):
        count = len(get_results(db, maxRows))
        data.append(count)
    return data


def make_fig():
    x = [100000*i for i in range(0, 11)]
    unigrams = get_data('unigrams.db')
    bigrams = get_data('bigrams.db')
    trigrams = get_data('trigrams.db')

    pyplot.plot(x, unigrams, label='Unigrams')    
    pyplot.plot(x, bigrams, label='Bigrams')
    pyplot.plot(x, trigrams, label='Trigrams')
    pyplot.xlabel('URLs crawled')
    pyplot.ylabel('Censored domains')
    pyplot.legend(loc='lower right', prop={'size': 10})
    pyplot.savefig('urls-crawled.png')
    

if __name__ == "__main__":
    make_fig()
