import heapq
import csv
import sqlite3
import matplotlib
import numpy as np
from matplotlib import pyplot
from operator import itemgetter


def get_data():
    conn = sqlite3.connect('../../../src/censor-search.db')
    c = conn.cursor()

    top_1000 = []
    i = 1
    with open ('../../../lists/top-1m.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csvreader:
            if i < 1000:
                top_1000.append(row[1])
                i += 1
            else:
                break
            

    data = {}
    c.execute('select distinct domain from urls where censored=1 and iteration>0')
    rows = c.fetchall()
    for row in rows:
        domain = row[0]
        contained = False
        for top_domain in top_1000:
            if top_domain in domain:
                contained = True
                break
            
        if not contained:
            count = c.execute('select count(1) from urls where domain=?',
                                  (domain,)).fetchone()[0]
            if domain[:4] == 'www.':
                domain = domain[4:]
            data[domain] = count
    conn.close()

    data = dict(heapq.nlargest(25, data.items(), key=itemgetter(1)))
    print(data)
    return data


def make_fig():
    data = get_data()
    domains = list(data.keys())
    counts = list(data.values())
    y_pos = np.arange(len(domains))
    pyplot.figure(figsize=(10,5))
    pyplot.bar(y_pos, counts)
    pyplot.ylabel('Filtered URLs')
    pyplot.xticks(y_pos, domains, rotation=55, ha='right')
    pyplot.subplots_adjust(bottom=0.25)
    pyplot.tick_params(axis='x', which='major', labelsize=9)
    pyplot.savefig('top-domains.png')
    

if __name__ == "__main__":
    get_data()
    make_fig()
