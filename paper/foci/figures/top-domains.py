import heapq
import json
import csv
import sqlite3
import matplotlib
import numpy as np
from matplotlib import pyplot
from operator import itemgetter
from collections import Counter


def get_data(db):
    conn = sqlite3.connect('../../../src/db/' + db)
    c = conn.cursor()

    # Get Alexa Top 1000 domains
    top_1000 = []
    i = 1
    with open ('../../../lists/alexa.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csvreader:
            if i < 1000:
                top_1000.append(row[1])
                i += 1
            else:
                break
            
    # Get the URL counts for each domain, excluding Alexa Top 1000
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

    # Return the top 25 domains
    data = dict(heapq.nlargest(25, data.items(), key=itemgetter(1)))
    print(data)
    return data


def make_fig():
    # Get the top 25 domains across unigrams, bigrams, and trigrams, sorted
    # unigram_data = get_data('unigrams.db')
    # bigram_data = get_data('bigrams.db')
    # trigram_data = get_data('trigrams.db')
    # all_data = Counter(unigram_data) + Counter(bigram_data) + Counter(trigram_data)
    # json.dump(all_data, open('figures/top_domains.json','w'))
    all_data = json.load(open('top-domains.json'))
    all_data = dict(heapq.nlargest(25, all_data.items(), key=itemgetter(1)))
    print(all_data)

    # Make a bar plot
    domains = list(all_data.keys())
    counts = list(all_data.values())
    y_pos = np.arange(len(domains))
    pyplot.figure(figsize=(10,5))
    pyplot.bar(y_pos, counts)
    pyplot.ylabel('Filtered URLs')
    pyplot.xticks(y_pos, domains, rotation=45, ha='right')
    pyplot.subplots_adjust(bottom=0.25)
    pyplot.tick_params(axis='x', which='major', labelsize=9)
    pyplot.savefig('top-domains.png')
    

if __name__ == "__main__":
    make_fig()
