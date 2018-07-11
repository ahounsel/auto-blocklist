import sys
import heapq
import csv
import sqlite3
import matplotlib
import numpy as np
from matplotlib import pyplot
from operator import itemgetter
sys.path.append('../../../src/')
from results import *

BIN_SIZE = 100000

def get_my_data(db):
    domains = get_results(db, 1000000)
    
    top_1m = {}
    with open ('../../../lists/alexa.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csvreader:
            domain = row[1]
            pos = int(row[0])
            top_1m[domain] = pos

    data = [0 for i in range(11)]
    for domain in domains:
        contained = False
        for top_domain in top_1m:
            if top_domain in domain:
                contained = True
                if top_1m[top_domain] > 1000:
                    bin = int(top_1m[top_domain] / BIN_SIZE)
                    data[bin] += 1
                break
        if not contained:
            data[10] += 1
        
    return data

def get_filteredweb_data():
    with open(BASE_DIR + 'lists/filteredweb.txt', 'r') as f:
        domains = f.read().splitlines()
    
    top_1m = {}
    with open ('../../../lists/top-1m.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csvreader:
            domain = row[1]
            pos = int(row[0])
            top_1m[domain] = pos

    data = [0 for i in range(11)]
    for domain in domains:
        contained = False
        for top_domain in top_1m:
            if top_domain in domain:
                contained = True
                if top_1m[top_domain] > 1000:
                    bin = int(top_1m[top_domain] / BIN_SIZE)
                    data[bin] += 1
                break
        if not contained:
            data[10] += 1
        
    return data


def make_fig():
    unigrams = get_my_data('unigrams.db')    
    bigrams = get_my_data('bigrams.db')
    trigrams = get_my_data('trigrams.db')
    pyplot.figure(figsize=(10,5))
    x = np.arange(10)
    xticks = ("100k-200k", "200k-300k",
              "300k-400k", "400k-500k", "500k-600k",
              "600k-700k", "700k-800k", "800k-900k",
              "900k-1m", "> 1m")
    pyplot.bar(x, unigrams[1:], 0.22, label='Unigrams')
    pyplot.bar(x + 0.22, bigrams[1:], 0.22, label='Bigrams')
    pyplot.bar(x + 0.44, trigrams[1:], 0.22, label='Trigrams')
    pyplot.xlabel('Position in Alexa Top 1 Million', labelpad=10) 
    pyplot.ylabel('Count')
    pyplot.legend(loc='upper right', prop={'size': 8})
    pyplot.xticks(x + 0.22, xticks, rotation='45')
    pyplot.tick_params(axis='x', which='major', labelsize=7)
    pyplot.subplots_adjust(bottom=0.2)
    pyplot.savefig('alexa.png')
    

if __name__ == "__main__":
    make_fig()
