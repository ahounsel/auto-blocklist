import sys
import requests
import nltk
from requests.exceptions import *
from bs4 import BeautifulSoup
from bs4.element import Comment
from nltk.tokenize.stanford import CoreNLPTokenizer
from nltk.collocations import *


def tag_visible(element):
    "True is the HTML tag is visible on the webpage, False otherwise"
    
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    elif isinstance(element, Comment):
        return False
    return True


def text_from_html(html):
    "Extract text from visible HTML content"
    
    soup = BeautifulSoup(html, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    text =  ' '.join(t.strip() for t in visible_texts)
    return text


def fetch_grams(url):
    "Fetch a webpage and return the text as unigrams and bigrams"

    sttok = CoreNLPTokenizer('http://localhost:9001')
    print(url)
    try:
        r = requests.get(url, timeout=5)
    except:
        print(sys.exc_info()[1])
        exit(-1)
    r.encoding = 'utf-8'
    html = r.text
    text = text_from_html(html)
    unigrams = sttok.tokenize(text)
    bigrams = bigrams_to_str(list(nltk.bigrams(unigrams)))
    trigrams = trigrams_to_str(list(nltk.trigrams(unigrams)))
    return (unigrams, bigrams, trigrams)


def bigrams_to_str(bigrams):
    "Convert bigram tuples to strings"
    
    b = []
    for bigram in bigrams:
        b.append(bigram[0] + ' ' + bigram[1])
    return b


def trigrams_to_str(trigrams):
    "Convert trigram tuples to strings"
    
    t = []
    for trigram in trigrams:
        t.append(trigram[0] + ' ' + trigram[1] + ' ' + trigram[2])
    return t
