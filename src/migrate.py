import sqlite3
import json
from tag import *
from search import *
from urllib.parse import urlparse


#DB_NAME = 'censor-search.db'
#DB_NAME = 'bigrams.db'
DB_NAME = 'test.db'


def create_tables():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('CREATE TABLE tags (tag text PRIMARY KEY, used integer, count integer, ' +
              'iteration integer)')
    c.execute('CREATE TABLE urls (url text PRIMARY KEY, domain text, used integer, ' +
              'censored integer, iteration integer, tag text)')

    conn.commit()
    conn.close()

    
def drop_tables():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('DROP TABLE urls')
    c.execute('DROP TABLE tags')

    conn.commit()
    conn.close()

    
def migrate():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    bigrams = c.execute('select * from bigrams').fetchall()
    unigrams = c.execute('select * from tags_cn').fetchall()
    tag_cnt = {}

    # Populate url table
    for row in bigrams:
        url = row[0]
        tag_cnt[url] = 0
        domain = url_to_domain(url)
        vals = (url, domain, 1, 1, 0)
        c.execute('INSERT INTO urls VALUES (?,?,?,?,?,"")', vals)

    # Add Chinese bigrams to tags table
    for row in bigrams:
        url = row[0]
        cn_bigrams = json.loads(row[2])
        for bigram in cn_bigrams:
            if url in tag_cnt and tag_cnt[url] < 10:
                bigram_split = bigram.split(' ')
                vals = (bigram_split[0] + '' + bigram_split[1], 0, 1, 0)
                c.execute('INSERT INTO tags VALUES (?,?,?,?)', vals)
                tag_cnt[url] += 1

    # Add Chinese unigrams to tags table
    for row in unigrams:
        url = row[0]
        unigrams = json.loads(row[1])
        for unigram in unigrams:
            if url in tag_cnt and tag_cnt[url] < 10 and isChinese(unigram):
                vals = (unigram, 0, 1, 0)
                c.execute('INSERT INTO tags VALUES (?,?,?,?)', vals)
                tag_cnt[url] += 1

    # Add English bigrams to tags table
    for row in bigrams:
        url = row[0]
        en_bigrams = json.loads(row[1])
        for bigram in en_bigrams:
            if url in tag_cnt and tag_cnt[url] < 10:
                vals = (bigram, 0, 1, 0)
                c.execute('INSERT INTO tags VALUES (?,?,?,?)', vals)
                tag_cnt[url] += 1

    conn.commit()
    conn.close()


def init_test_db():
    conn_cs = sqlite3.connect('censor-search.db')
    conn_test = sqlite3.connect(DB_NAME)
    cur_cs = conn_cs.cursor()
    cur_test = conn_test.cursor()

    rows = cur_cs.execute(('select * from urls where iteration=0 ' +
                           'and censored=1')).fetchall()
    for row in rows:
        vals = row + ("N/A",)
        cur_test.execute('insert into urls values (?,?,?,?,?,?)', vals)
        print(vals)
    conn_test.commit()
    conn_test.close()
    conn_cs.close()


def migrate_itr5_urls():
    conn_bigrams = sqlite3.connect('bigrams.db')
    conn_corrupt = sqlite3.connect('bigrams-corrupt.db')
    c_bigrams = conn_bigrams.cursor()
    c_corrupt = conn_corrupt.cursor()

    rows = c_corrupt.execute('select * from urls where iteration=5').fetchall()
    urls = []
    for row in rows:
        r = (row[0], row[1], 0, 0, 5, row[5])
        urls.append(r)
        print(r)
    c_bigrams.executemany('insert into urls values (?,?,?,?,?,?)', urls)
    conn_bigrams.commit()
    conn_bigrams.close()
    conn_corrupt.close()
    

if __name__ == "__main__":
     drop_tables()
     create_tables()
#     migrate()
     init_test_db()
#    migrate_itr5_urls()
