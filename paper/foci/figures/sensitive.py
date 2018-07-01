import json
import sys
import heapq
import csv
import sqlite3
import matplotlib
from matplotlib import pyplot
from operator import itemgetter
sys.path.append('../../../src/')
from search import *
from tag import *


def write_data(db):
    data = json.load(open('%s.txt' % db))
    with open('%s.csv' % db, 'w') as my_file:
        writer = csv.writer(my_file)
        writer.writerows(list(data.items())[:25])


# def make_fig(out):
#     data = json.load(open('%s.txt' % out))
#     tags = list(data.keys())
#     counts = list(data.values())
#     pyplot.figure(figsize=(5,8))
#     pyplot.barh(tags, counts)
#     pyplot.xlabel('% of URLs filtered')
#     pyplot.tick_params(axis='y', which='major', labelsize=6)
#     pyplot.savefig('sensitive-%s.png' % out, bbox_inches='tight')
    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python3 fig10.py [bigrams|trigrams]')
        exit(-1)
    out = sys.argv[1]
    write_data(out)
