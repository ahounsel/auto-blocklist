import sys
import csv
import tldextract
import sqlite3


BASE_DIR = '/home/ahounsel/git/censor-seeker/'


def count_new_domains(itr, db):
    "Count the amount of new censored domains found"

    conn = sqlite3.connect(BASE_DIR + 'src/db/' + db)
    c = conn.cursor()

    rows = c.execute(('select distinct domain from urls where censored=1 ' +
                     'and iteration=?'), (itr,)).fetchall()
    itr_domains = [domain[0] for domain in rows]
    rows = c.execute(('select distinct domain from urls where censored=1 ' +
                     'and iteration<?'), (itr,)).fetchall()
    not_itr_domains = [domain[0] for domain in rows]
    diff = list(set(itr_domains) - set(not_itr_domains))
    str = 'New domains found on itr {0}: {1}'.format(itr, len(diff))
    print(str)
    conn.close()


def get_results(db, maxRows):
    print(BASE_DIR + 'src/db/' + db)
    conn = sqlite3.connect(BASE_DIR + 'src/db/' + db)
    c = conn.cursor()

    rows = c.execute('select distinct domain from urls where censored=1 '
                     + 'and rowid <= ?', (maxRows,)).fetchall()
    domains = [domain[0] for domain in rows]
    domains = sorted(domains)

    # Load Alexa Top 1000 domains
    top_1000 = []
    i = 0
    with open (BASE_DIR + 'lists/alexa.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csvreader:
            if i < 1000:
                top_1000.append(row[1])
                i += 1
            else:
                break
            
    # Count censored domains that are not in Alexa Top 1000
    results = []
    for domain in domains:
        ext = tldextract.extract(domain)
        cleaned_domain = '.'.join(part for part in ext if part and part != 'www')        
        contained = False
        for top_domain in top_1000:
            if top_domain in cleaned_domain:
                contained = True
                break
        if not contained and domain not in results:
            results.append(cleaned_domain)
            
    conn.close()
    return results


def get_unique_urls(maxRows):
    bigram_conn = sqlite3.connect(BASE_DIR + 'src/db/' + 'bigrams.db')
    trigram_conn = sqlite3.connect(BASE_DIR + 'src/db/' + 'trigrams.db')
    bigram_cursor = bigram_conn.cursor()
    trigram_cursor = trigram_conn.cursor()

    bigram_urls = bigram_cursor.execute('select url from urls where rowid <= ?',
                                        (maxRows,)).fetchall()
    trigram_urls = trigram_cursor.execute('select url from urls where rowid <= ?',
                                          (maxRows,)).fetchall()
    urls_in_common = set(bigram_urls) | set(trigram_urls)
    print(len(urls_in_common))


def compare_results(db):
    my_results = set(get_results(db, 1000000))
    with open(BASE_DIR + 'lists/filteredweb.txt', 'r') as f:
        filteredweb_results = set(f.read().splitlines())
    difference = sorted(my_results - filteredweb_results)
        
    print(db)
    print('# of censored domains found by CensorSearch (w/o Top 1000):', len(my_results))
    print('# of censored domains found by FilteredWeb:', len(filteredweb_results))
    print('Length of the set difference:', len(difference))
    print()
    return difference

     
if __name__ == "__main__":
    unigram_results = sorted(compare_results('unigrams.db'))
    bigram_results = sorted(compare_results('bigrams.db'))
    trigram_results = sorted(compare_results('trigrams.db'))
    total_results = sorted(set(unigram_results) | set(bigram_results) | set(trigram_results))
    print('Total # of censored domains discovered:', len(total_results))

    with open('unigram_list.txt', 'w') as blocklist:
        for domain in unigram_results:
            blocklist.write(domain + '\n')

    with open('bigram_list.txt', 'w') as blocklist:
        for domain in bigram_results:
            blocklist.write(domain + '\n')

    with open('trigram_list.txt', 'w') as blocklist:
        for domain in trigram_results:
            blocklist.write(domain + '\n')

    with open('total_list.txt', 'w') as blocklist:
        for domain in total_results:
            blocklist.write(domain + '\n')
