import sys
import csv
import json
import sqlite3
from fetch import *
from tag import *
from sqlite3 import OperationalError


LIST_CN = '../lists/cn-blocked.csv'
CREATE_UNIGRAMS = 'CREATE TABLE unigrams (url text, en_unigrams, cn_unigrams)'
CREATE_BIGRAMS  = 'CREATE TABLE bigrams (url text, en_bigrams, cn_bigrams)'
INSERT_UNIGRAMS = 'INSERT INTO unigrams VALUES (?,?,?)'
INSERT_BIGRAMS  = 'INSERT INTO bigrams VALUES (?,?,?)'


def seed_unigrams():
    "Seed the system for unigrams with the Chinese test list from Citizen Lab"

    conn = sqlite3.connect('censor-search.db')
    c = conn.cursor()

    try:
        c.execute(CREATE_UNIGRAMS)
    except OperationalError:
        print('Table already exists')

    with open(LIST_CN, 'r') as list:
        csvreader = csv.reader(list, delimiter=',')  
        next(csvreader)                              # Skip the CSV header
        for row in csvreader:
            category = row[1]
            if category != "MILX":                   # Don't fetch terror websites
                try:
                    url = row[0]
                    print(url)
                    grams = fetch_grams(url)
                    unigrams = tf_idf(grams[0], True)
                    print(unigrams)
                    unigrams_en = json.dumps(unigrams[0])
                    unigrams_cn = json.dumps(unigrams[1])
                    vals = (url, unigrams_en, unigrams_cn)
                    c.execute(INSERT_UNIGRAMS, vals)
                    conn.commit()
                except:
                    print('Error:', sys.exc_info()[1])

    conn.close()
    

def seed_bigrams():
    "Seed the system for bigrams with the Chinese test list from Citizen Lab"

    conn = sqlite3.connect('censor-search.db')
    c = conn.cursor()

    try:
        c.execute(CREATE_BIGRAMS)
    except OperationalError:
        print('Table already exists')

    with open(LIST_CN, 'r') as list:
        csvreader = csv.reader(list, delimiter=',')  
        next(csvreader)                              # Skip the CSV header
        for row in csvreader:
            category = row[1]
            if category != "MILX":                   # Don't fetch terror websites
                try:
                    url = row[0]
                    print(url)
                    grams = fetch_grams(url)
                    bigrams = tf_idf(grams[1], False)
                    print(bigrams)
                    bigrams_en = json.dumps(bigrams[0])
                    bigrams_cn = json.dumps(bigrams[1])
                    vals = (url, bigrams_en, bigrams_cn)
                    c.execute(INSERT_BIGRAMS, vals)
                    conn.commit()
                except:
                    print('Error:', sys.exc_info()[1])

    conn.close()

    
if __name__ == "__main__":
    argc = len(sys.argv)
    if argc < 2 or not (sys.argv[1] == 'unigrams' or sys.argv[1] == 'bigrams'):
        print('Usage: python3 seed.py [unigrams | bigrams]')
        exit(-1)

    if sys.argv[1] == 'unigrams':
        seed_unigrams()
    elif sys.argv[1] == 'bigrams':
        seed_bigrams()        
