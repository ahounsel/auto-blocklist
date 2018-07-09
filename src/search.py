import sys
import json
import requests
import sqlite3
import time
import dns.resolver
import threading
import csv
import time
import multiprocessing
import queue
from dns.exception import Timeout
from xml.etree import ElementTree
from urllib.parse import urlparse
from tag import *
from fetch import *
from results import *


#DB_NAME = 'db/bigrams.db'
# DB_NAME = 'db/trigrams.db'
DB_NAME = 'db/unigrams.db'
KEYS = 'KEYS'

THREADS = 32
PROCESSES = 32

url_queue = multiprocessing.Queue()
tag_queue = multiprocessing.Queue()
censored_queue = multiprocessing.Queue()


def read_keys(keys_filename):
    try:
        with open(keys_filename) as keys_file:
            keys = json.load(keys_file)
            return keys
    except IOError as err:
        print(err)
        exit(-1)


def call_api(url, headers, params):
    "Performs an API call"
    
    try:
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
    except HTTPError:
        print('Couldn\'t get the response from Microsoft Azure')
    except:
        print('Error:', sys.exc_info()[0]) 
    return r

    
def translate_to_cn(term, translator_keys):
    "Translate a term from English to Chinese"

    params = {'from': 'en',
              'to': 'zh'}
    
    params['text'] = term
    payload = call_api(translator_keys["url"], translator_keys["headers"], params)
    translation = ElementTree.fromstring(payload.text).text
    return translation


def translate_to_en(term, translator_keys):
    "Translate a term from Chinese to English"

    params = {'from': 'zh',
              'to': 'en'}
    
    params['text'] = term
    payload = call_api(translator_keys["url"], translator_keys["headers"], params)
    translation = ElementTree.fromstring(payload.text).text
    return translation

        
def search(tag, search_keys):
    "Use a tag to search for candidate"

    if tag is None:
        print('Tag is NoneType')
        webpages = {}

    params = {'safeSearch': 'off',
              'mkt':        'en-us',    # Repeat experiments with Chinese market
              'count':      '50'}
    params['q'] = (tag + ' NOT (site:blogspot.com) NOT (site:blogspot.tw)' 
                       + ' NOT (site:blogspot.fr) NOT (site:blogspot.jp)'
                       + ' NOT (site:tumblr.com) NOT (site:youtube.com)'
                       + ' NOT (site:facebook.com) NOT (site:twitter.com)')
    payload = call_api(search_keys["url"], search_keys["headers"], params).json()
    if 'webPages' in payload and 'value' in payload['webPages']:
        webpages = payload['webPages']['value']
    else:
        webpages = {}
    return webpages

        
def is_censored(domain):
    "Determine if a domain is censored in China"
    
    resolver = dns.resolver.Resolver()
    # resolver.nameservers = ['220.181.57.217', '223.96.100.100', '1.24.10.10',
    #                         '202.143.16.100', '180.160.10.1', '180.77.100.200',
    #                         '144.0.111.90', '42.101.0.1']
    resolver.nameservers = ['220.181.57.218']
    resolver.lifetime = 3.0
        
    try:
        answer = resolver.query(domain, 'A')
        return True
    except dns.exception.Timeout:
        return False
    except:
        print('Error:', sys.exc_info()[0])
        return False


def url_to_domain(url):
    "Extract the domain name from a URL"
    
    parsed_uri = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    return domain


def censor_producer(domains, itr):
    for d in domains:
        try:
            domain = d[0]
            if is_censored(domain):
                print('CENSORED: %s' % domain)
                censored_queue.put(domain)
            else:
                print('Not censored: %s' % domain)
        except:
            print('Error:', sys.exc_info()[1])
            continue


def censor_consumer(itr):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('update urls set censored=0, used=1 where iteration=?', (itr,))
    while True:
        try:
            domain = censored_queue.get(block=False)
            c.execute('update urls set censored=1, used=0 where domain=? and iteration=?', (domain,itr,))
            print(domain)
        except queue.Empty:
            print('Censored queue emptied')
            break
        except:
            print('Error:', sys.exc_info()[1])
            continue

    conn.commit()
    conn.close()


def tag_producer(censored_urls, itr):
    print(len(censored_urls))
    for row in censored_urls:
        url = row[0]
        try:
            unigrams = 0
            # bigrams = 0
            # trigrams = 0
            tags = []
            grams = fetch_grams(url)
            unigram_tags = tf_idf(grams[0], 1)
            # bigram_tags = tf_idf(grams[1], 2)
            # trigram_tags = tf_idf(grams[2], 3)
            # if trigram_tags[1] is not None and trigrams < MAX_TAGS:        # Chinese trigrams
            #     for cn_tag in trigram_tags[1]:
            #         if trigrams < MAX_TAGS:
            #             tags.append(cn_tag)
            #             trigrams += 1
            # if trigram_tags[0] is not None and trigrams < MAX_TAGS:        # English trigrams
            #     for en_tag in trigram_tags[0]:
            #         if trigrams < MAX_TAGS:
            #             tags.append(en_tag)
            #             trigrams += 1
            # if bigram_tags[1] is not None and bigrams < MAX_TAGS:        # Chinese bigrams
            #     for cn_tag in bigram_tags[1]:
            #         if bigrams < MAX_TAGS:
            #             tags.append(cn_tag)
            #             bigrams += 1
            # if bigram_tags[0] is not None and bigrams < MAX_TAGS:        # English bigrams
            #     for en_tag in bigram_tags[0]:
            #         if bigrams < MAX_TAGS:
            #             tags.append(en_tag)
            #             bigrams += 1
            if unigram_tags[1] is not None:        # Chinese unigrams
                for cn_tag in unigram_tags[1]:
                    if unigrams < MAX_TAGS:
                        tags.append(cn_tag)
                        unigrams += 1
            if unigram_tags[0] is not None:        # English unigrams
                for en_tag in unigram_tags[0]:
                    if unigrams < MAX_TAGS:
                        tags.append(en_tag)
                        unigrams += 1
            print(url, tags)
            vals = (url, tags, itr)
            tag_queue.put(vals)
        except:
            print('Error:', sys.exc_info()[1])
            continue


def tag_consumer():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    while True:
        try:
            tuple = tag_queue.get(block=False)
            url = tuple[0]
            tags = tuple[1]
            itr = tuple[2]
            for tag in tags:
                try:
                    vals = (tag, 0, 1, itr)
                    c.execute('INSERT INTO tags VALUES (?,?,?,?)', vals)
                    print(tag)
                except sqlite3.IntegrityError:
                    print('Duplicate tag:', tag)
            c.execute('UPDATE urls SET used=1 WHERE url=?', (url,))
        except queue.Empty:
            print('Queue emptied')
            break
        except:
            print('Error:', sys.exc_info()[1])
            continue
    conn.commit()
    conn.close()
    

def url_producer(unused_tags, itr, keys):
    "For each tag, search for candidate URLs"

    for row in unused_tags:
        try:
            tag = row[0]
            print(tag)
            if isEnglish(tag):
                translated_tag = translate_to_cn(tag, keys["translator_info"])
                search_results = search(translated_tag, keys["search_info"])
            else:
                search_results = search(tag, keys["search_info"])

            for result in search_results:
                url = result['url']
                parsed_uri = urlparse(url)
                domain = '{uri.netloc}'.format(uri=parsed_uri)
                # Ignore popular domains
                if not ('youtube' in domain or
                        'tumblr' in domain or
                        'blogspot' in domain or
                        'facebook' in domain or
                        'twitter' in domain):
                    vals = (url, domain, 0, 0, itr+1, tag)
                    url_queue.put(vals)
        except:
            print('Error:', sys.exc_info()[1])
            continue


def url_consumer():
    "Add search results from the queue to the db"
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    while True:
        try:
            tuple = url_queue.get(block=False)
            url = tuple[0]
            tag = tuple[5]
            try:
                c.execute('INSERT INTO urls VALUES (?,?,?,?,?,?)', tuple)
                print(url)
            except sqlite3.IntegrityError:
                print('Duplicate URL:', url)
            c.execute('UPDATE TAGS SET used=1 WHERE tag=?', (tag,))
        except queue.Empty:
            print('Queue emptied')
            break
        except:
            print('Error:', sys.exc_info()[1])
            continue
    conn.commit()
    conn.close()


def part_one(itr):
    "Test search results for censorship"

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    domains = c.execute(('select distinct domain from urls ' + 
                               'where iteration=?'), (itr,)).fetchall()
    print('# of distinct domains to test:', len(domains))
    conn.close()

    block_size = int(len(domains)/THREADS)
    blocks = [domains[i:i + block_size] for i in range(0, len(domains), block_size)]
    _args = [(block, itr) for block in blocks]
    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=censor_producer, args=_args[i])
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    censor_consumer(itr)

    
def part_two(itr):
    "Get the tags for newly found URLs that are censored"
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    censored_urls = c.execute(('select * from urls where ' +
                               'censored=1 and iteration=?'), (itr,)).fetchall()
    conn.close()

    block_size = int(len(censored_urls)/PROCESSES)
    blocks = [censored_urls[i:i + block_size] for i in range(0, len(censored_urls), block_size)]
    args = [(block, itr) for block in blocks]
    pool = multiprocessing.Pool(PROCESSES)
    pool.starmap(tag_producer, args)
    tag_consumer()

    
def part_three(itr, keys):
    "Search for candidate URLs using newly extracted tags"

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    unused_tags = c.execute(('select * from tags where used=0 ' +
                               'and iteration=?'), (itr,)).fetchall()
    print('# of unused tags to search with', len(unused_tags))
    conn.close()

    block_size = int(len(unused_tags)/PROCESSES)
    blocks = [unused_tags[i:i + block_size] for i in range(0, len(unused_tags), block_size)]
    args = [(block, itr, keys) for block in blocks]
    pool = multiprocessing.Pool(PROCESSES)
    pool.starmap(url_producer, args)
    url_consumer()
    
        
def find_censored_urls(keys):
    "Use seeded URLs to search for censored webpages"

    for i in range(2,3):
        itr = i
        print('Itr %d' % itr)
        part_two(itr)
        part_three(itr, keys)
        part_one(itr+1)


if __name__ == "__main__":
    keys = read_keys(KEYS)
    start = time.time()
    find_censored_urls(keys)
    end = time.time()
    print(end - start)
