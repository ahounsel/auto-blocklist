import math
import sys
import string
import requests
import heapq
import threading
import json
import concurrent.futures as cf
from json import decoder
from json.decoder import JSONDecodeError
from operator import itemgetter
from collections import Counter
from stopwords import *
from requests_futures.sessions import FuturesSession



EN_CORPUS_SIZE = 4541627
CN_CORPUS_SIZE = 302652

EN_URL = "http://phrasefinder.io/search?query=%s&corpus=eng-us"
CN_URL = "http://phrasefinder.io/search?query=%s&corpus=chi"

MAX_TAGS = 10


def isEnglish(s):
    "True if the string can be encoded in ASCII, false otherwise"
    
    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True

    
def isChinese(s):
    "True if the string consists entirely of Chinese characters, false otherwise"
    
    return all(u'\u4e00' <= c <= u'\u9fff' or c == ' ' for c in s)


def term_frequency(tokens):
    "Compute term frequency for each token"
    
    counter = Counter(tokens)
    page_len = len(tokens)
    tf = {}
    
    for term in counter:
        tf[term] = counter[term] / page_len
    return tf


def idf_unigrams(unigrams):
    "Compute inverse document frequency for each unigram"

    en_idf = {}
    cn_idf = {}
    unique = set(unigrams)

    for unigram in unique:
        try:
            english = isEnglish(unigram)
            chinese = isChinese(unigram)
            en_stopword = unigram in STOPWORDS_EN
            cn_stopword = unigram in STOPWORDS_CN
            punctuation = unigram in string.punctuation
            if english and not punctuation and not en_stopword:
                url = EN_URL % unigram
                r = requests.get(url).json()
                if 'phrases' in r and len(r['phrases']) != 0:
                    containing = r['phrases'][0]['vc']
                    en_idf[unigram] = math.log(EN_CORPUS_SIZE / (1 + containing))
            elif chinese and not punctuation and not cn_stopword:
                url = CN_URL % unigram
                r = requests.get(url).json()
                if 'phrases' in r and len(r['phrases']) != 0:
                    containing = r['phrases'][0]['vc']
                    cn_idf[unigram] = math.log(CN_CORPUS_SIZE / (1 + containing))
        except JSONDecodeError:
            continue
        except:
            print('idf_unigrams():', sys.exc_info()[0])
            continue
    return (en_idf, cn_idf)


def idf_bigrams(bigrams):
    "Compute inverse document frequency for each bigram"
    
    en_idf = {}
    cn_idf = {}
    unique = set(bigrams)
    session = FuturesSession(max_workers=50)
    en_futures = {}
    cn_futures = {}

    for bigram in unique:
        try:
            b = bigram.split(' ')
            english = isEnglish(b[0]) and isEnglish(b[1])
            chinese = isChinese(b[0]) and isChinese(b[1])
            contains_en_stopword = (b[0] in STOPWORDS_EN or 
                                    b[1] in STOPWORDS_EN)
            contains_cn_stopword = (b[0] in STOPWORDS_CN or 
                                    b[1] in STOPWORDS_CN)
            contains_punctuation = (b[0] in string.punctuation or
                                    b[1] in string.punctuation)
            if english and not contains_en_stopword and not contains_punctuation:
                url = EN_URL % (b[0] + ' ' + b[1])
                future = session.get(url)
                en_futures[future] = bigram
            elif chinese and not contains_cn_stopword and not contains_punctuation:
                url = CN_URL % (b[0] + ' ' + b[1])
                future = session.get(url)
                cn_futures[future] = bigram
        except:
            print('idf_bigrams():', sys.exc_info()[1])
            continue

    
    for future in cf.as_completed(en_futures, timeout=5):
        try:
            bigram = en_futures[future]
            response = future.result()
            r = json.loads(response.content.decode('utf-8'))
            if 'phrases' in r and len(r['phrases']) != 0:
                containing = r['phrases'][0]['vc']
                en_idf[bigram] = math.log(EN_CORPUS_SIZE / (1 + containing))
        except JSONDecodeError:
            continue
        except:
            print('idf_bigrams():', sys.exc_info()[1])
    for future in cf.as_completed(cn_futures, timeout=5):
        try:
            bigram = cn_futures[future]
            response = future.result()
            r = json.loads(response.content.decode('utf-8'))
            if 'phrases' in r and len(r['phrases']) != 0:
                containing = r['phrases'][0]['vc']
                cn_idf[bigram] = math.log(CN_CORPUS_SIZE / (1 + containing))
        except JSONDecodeError:
            continue
        except:
            print('idf_bigrams():', sys.exc_info()[1])

    return(en_idf, cn_idf)


def idf_trigrams(trigrams):
    "Compute inverse document frequency for each trigram"
    
    en_idf = {}
    cn_idf = {}
    unique = set(trigrams)
    session = FuturesSession(max_workers=50)
    en_futures = {}
    cn_futures = {}

    for trigram in unique:
        try:            
            t = trigram.split(' ')
            english = isEnglish(t[0]) and isEnglish(t[1]) and isEnglish(t[2])
            chinese = isChinese(t[0]) and isChinese(t[1]) and isChinese(t[2])
            contains_en_stopword = (t[0] in STOPWORDS_EN or
                                    t[1] in STOPWORDS_EN or
                                    t[2] in STOPWORDS_EN)
            contains_cn_stopword = (t[0] in STOPWORDS_CN or
                                    t[1] in STOPWORDS_CN or
                                    t[2] in STOPWORDS_CN)
            contains_punctuation = (t[0] in string.punctuation or
                                    t[1] in string.punctuation or
                                    t[2] in string.punctuation)
            if english and not contains_punctuation and not contains_en_stopword:
                url = EN_URL % (t[0] + ' ' + t[1] + ' ' + t[2])
                future = session.get(url)
                en_futures[future] = trigram
            elif chinese and not contains_punctuation and not contains_cn_stopword:
                url = CN_URL % (t[0] + ' ' + t[1] + ' ' + t[2])
                future = session.get(url)
                cn_futures[future] = trigram
        except:
            print('idf_trigrams():', sys.exc_info()[0])
            continue

    for future in cf.as_completed(en_futures, timeout=5):
        try:
            trigram = en_futures[future]
            response = future.result()
            r = json.loads(response.content.decode('utf-8'))
            if 'phrases' in r and len(r['phrases']) != 0:
                containing = r['phrases'][0]['vc']
                en_idf[trigram] = math.log(EN_CORPUS_SIZE / (1 + containing))
        except JSONDecodeError:
            continue
        except:
            print('idf_trigrams():', sys.exc_info()[1])
    for future in cf.as_completed(cn_futures, timeout=5):
        try:
            trigram = cn_futures[future]
            response = future.result()
            r = json.loads(response.content.decode('utf-8'))
            if 'phrases' in r and len(r['phrases']) != 0:
                containing = r['phrases'][0]['vc']
                cn_idf[trigram] = math.log(CN_CORPUS_SIZE / (1 + containing))
        except JSONDecodeError:
            continue
        except:
            print('idf_trigrams():', sys.exc_info()[1])

    return(en_idf, cn_idf)


def tf_idf(tokens, ngram_len):
    "Compute TF-IDF for each token"

    en_tf_idf = {}
    cn_tf_idf = {}
    
    if ngram_len == 1:
        idf = idf_unigrams(tokens)
    elif ngram_len == 2:
        idf = idf_bigrams(tokens)
    elif ngram_len == 3:
        idf = idf_trigrams(tokens)

    tf = term_frequency(tokens)
    en_idf = idf[0]
    cn_idf = idf[1]
    
    for token in en_idf:
        en_tf_idf[token] = tf[token] * en_idf[token]
    for token in cn_idf:
        cn_tf_idf[token] = tf[token] * cn_idf[token]
        
    en_tf_idf = dict(heapq.nlargest(MAX_TAGS, en_tf_idf.items(), key=itemgetter(1)))
    cn_tf_idf = dict(heapq.nlargest(MAX_TAGS, cn_tf_idf.items(), key=itemgetter(1)))

    return (en_tf_idf, cn_tf_idf)
