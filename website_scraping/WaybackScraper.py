#!/apps/anaconda3/bin/python3
"""
Author: Romain Boulland, Thomas Bourveau, Matthias Breuer
Date: Jun 24, 2021
Code: Generate bag of words for a time-series of company websites

* Please customize the config file before launching the program *

* Download the following nltk corpus before running the program *
nltk.download('stopwords')
nltk.download('punkt')
"""


# %% Packages
import sys
import config
import re
import json
import time
import nltk
import string
import itertools
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import Counter

# %% Macros
STATUS_CODE = config.status_code
MIME_TYPE = config.mime_type
HEADERS = config.headers
MAX_URL = config.max_url
MAX_SUB = config.max_sub
PARSER = config.parser
RAW = config.raw
BOW_OPTIONS = config.bow_options
PATH = config.path

# %% Functions
"""
The function wayback_query() interacts with the Wayback Machine API to retrieve all matched results for a given input URL.
The official documentation of the API is here: https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server
"""


def wayback_query(host, match_type='exact', collapse_time=10):
    # Wayback API query
    q = 'http://web.archive.org/cdx/search/cdx?url={}&matchType={}&collapse=timestamp:{}&output=json' \
        .format(host, match_type, collapse_time)
    r = requests.get(q)
    # Convert json format result into a dataframe
    df = pd.read_json(r.content)
    # If no match
    if df.shape[0] == 0:
        print('Wayback does not archive URLs under {}.'.format(host))
        return None
    # If matches returned
    else:
        # First row is column index
        df.columns = df.iloc[0]
        df = df.drop(df.index[0]).reset_index(drop=True)
        print('{} matched URLs found under {}.'.format(df.shape[0], host))
        # Search results cleaning: timestamp\
        # Drop observations with invalid timestamps
        df['datetime'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H%M%S', errors='coerce')
        if df['datetime'].isnull().any():
            df = df[df['datetime'].notnull()]
            print('{} matches left after dropping invalid timestamps.'.format(df.shape[0]))
        # Search results cleaning: urlkey
        # Ensure uniqueness of urlkey, keep the shortest if not
        if df['urlkey'].nunique() > 1:
            df = df[df['urlkey'] == sorted(df['urlkey'].values, key=len)[0]]
            print('Urlkey not unique, keep the shortest, {} matches left.'.format(df.shape[0]))
        # Complete url for archived websites (as stored on archive.org)
        df['url'] = ['https://web.archive.org/web' + '/' + t + '/' + o for t, o in
                     zip(df['timestamp'].values, df['original'].values)]
        df.sort_values(['urlkey', 'datetime'], inplace=True)
        # Output a txt if specified
        return df


"""
The function query_filter() refines search results by applying the following filters:
    - Frequency
    - Date range: Optional
    - Status code: Default
    - MIME type: Default
"""


def query_filter(df, freq, date_range=None):
    # Filtering search results: date range, status code, MIME type
    if date_range:
        df = df[(df['datetime'] >= pd.to_datetime(date_range[0])) &
                (df['datetime'] <= pd.to_datetime(date_range[1]))]
    """
    The following filters are deprecated
    A given non-200 URL may be redirected to a valid URL
    Filters applied later based on the final destination
    df = df[df['statuscode'].isin(status_code)]
    df = df[df['mimetype'].apply(lambda x: any([re.search(y, x) for y in mime_type]))]
    """
    # Reset index
    df = df.reset_index(drop=True)
    # Resample the time-series of search results at desired frequency
    df['length'] = pd.to_numeric(df['length'], errors='coerce')
    df_r = df.set_index('datetime').resample(freq)['length'].mean().to_frame().reset_index()
    df_r.columns = ['agg_datetime', 'avg_length']
    df_r['period'] = df_r['agg_datetime'].dt.to_period(freq)
    df['period'] = df['datetime'].dt.to_period(freq)
    df = pd.merge(df, df_r, on=['period'], how='inner')
    df = df.sort_values(['datetime']).drop_duplicates(['period'], keep='last')
    # Print filtering result
    print('{} matches left after filtering.'.format(df.shape[0]))
    # Return filtered dataframe
    return df


"""
The function wayback_urlparse() parses the timestamp and original URL for URLs seen during scraping
"""


def wayback_urlparse(url):
    # Obtain timestamp and original URL for an archived URL
    if re.search('https://web.archive.org/web/[0-9]{14}/', url):
        timestamp = re.search('[0-9]{14}', url)[0]
        original = re.sub('https://web.archive.org/web/[0-9]{14}/', '', url)
        return timestamp, original
    else:
        return None, None


"""
The function url_scrape() scrapes the URL and returns an array of outputs including: 
    - HTML text
    - Sub-URLs
    - Error description if occurred
    - Processing time
"""


def url_scrape(url, status_code=STATUS_CODE, mime_type=MIME_TYPE, raw=RAW, headers=HEADERS, parser=PARSER):
    # Dictionary to store parsing results & errors
    url_res = {'URL': url,
               'cURL': url,
               'error': None,
               'subURLs': [],
               'text': ''}
    if raw:
        url_res['raw'] = ''

    # Request the URL and retrieve status code, mime type, and raw text
    try:
        # Open the sent URL using requests.get()
        curr_request = requests.get(url, headers=headers, allow_redirects=True)
    except Exception as ex_request:
        # Print the exception if requests() fails
        # Mostly due to connection failure or exceeding maximum retries
        url_res['error'] = str(ex_request)
        return url_res

    # The current URL and its timestamp % original
    # May not be the same with the sent URL due to redirection
    curr_url = curr_request.url
    url_res['cURL'] = curr_url
    # Check the status code
    curr_code = curr_request.status_code
    # Check the mime type
    curr_type = curr_request.headers['Content-Type']
    # Open the url and get raw text
    curr_html = curr_request.text
    # Store the raw html text if specified
    if raw:
        url_res['raw'] = curr_html

    # Check status code and MIME type
    try:
        assert str(curr_code) in status_code, 'Invalid HTTP status code: ' + str(curr_code)
        assert any([re.search(x, curr_type) for x in mime_type]), 'Invalid MIME type: ' + str(curr_type)
    except Exception as ex_response:
        url_res['error'] = str(ex_response)
        return url_res

    # Create soup object to remove HTML tags
    curr_soup = BeautifulSoup(curr_html, parser)
    # Kill all script and style elements
    for script in curr_soup(['script', 'style']):
        script.decompose()
    # Kill Wayback bars
    for div_id in ['wm-ipp-base', 'wm-ipp-print', 'donato']:
        for div in curr_soup.find_all('div', id=div_id):
            div.decompose()
    # Body text of the html
    try:
        curr_text = curr_soup.body.get_text()
        url_res['text'] = curr_text
    except Exception as ex_text:
        url_res['error'] = str(ex_text)

    # Get sub-URLs of the URL
    sub_urls = []
    for tag in curr_soup.find_all('a', href=True):
        # Extract the links in the URL
        sub_url = tag['href']
        # Join the sub-URL with the current URL
        # Use the actual current URL instead of the sent URL
        sub_url = urljoin(curr_url, sub_url)
        # Store the sub-URL in a list
        sub_urls.append(sub_url)
    url_res['subURLs'] = sub_urls

    # Print error if there is one
    if url_res['error'] is not None:
        print(url_res['error'])
    # Return a dictionary object for scraping result
    return url_res


"""
The function tree_scrape() scrapes a tree of URLs where the sent URL is the root.
User needs to specify the max number of URLs (max_url) and/or the max level of sub-URLs (max_sub)
The function stops when either of the two thresholds is exceeded
"""


def tree_scrape(url, max_url=MAX_URL, max_sub=MAX_SUB):
    # Start time
    start_time = time.time()

    # List to store all scraping results
    tree_res = []

    # Dictionaries to track the tree structure
    # urls_dict: FIFO dictionary sorted by sub-URL level
    # seen_dict: dictionary stored all seen URLs
    urls_dict = {url: 0}
    seen_dict = {url: {'sub': 0, 'info': wayback_urlparse(url)}}

    # Navigate the tree
    sub = 0
    while len(urls_dict) > 0 and len(tree_res) < max_url and sub <= max_sub:
        # Get the current URL
        # Pop the one with the lowest sub-level
        curr_url = sorted(urls_dict.items(), key=lambda x: x[1], reverse=False).pop(0)[0]
        # Remove it from the dictionary of all URLs
        urls_dict.pop(curr_url)

        # Parse the current URL
        url_res = url_scrape(curr_url)
        # Add sub-level to parsing result
        url_res['sub'] = seen_dict[curr_url]
        # Add to the list of opened URLs
        tree_res.append(url_res)

        # Get sub-URLs of the current URL
        for sub_url in url_res['subURLs']:
            # If sub_url is not in seen, then add it along with its level to urls(dict) and seen(dict)
            sub_timestamp, sub_original = wayback_urlparse(sub_url)
            if sub_original is not None and sub_original not in [v['info'][1] for v in seen_dict.values()]:
                urls_dict[sub_url] = seen_dict[curr_url]['sub'] + 1
                seen_dict[sub_url] = {'sub': urls_dict[sub_url], 'info': (sub_timestamp, sub_original)}

        # Current level of sub-URL
        sub = min(urls_dict.values(), default=max([v['sub'] for v in seen_dict.values()]))

        # Random waiting time before the next request
        time.sleep(1)

    # End time
    end_time = time.time()

    # Print scraping progress
    print('URL %s finished scraping in %.2f seconds. '
          '%d URLs seen. %d opened. %d returned errors. '
          'Stop at level %d sub-URLs.' %
          (url, end_time - start_time,
           len(seen_dict), len(tree_res), len([d for d in tree_res if d['error'] is not None]),
           sub)
          )

    # Return list of scraping results
    return tree_res


"""
The function text_tokenize() preprocesses and tokenizes text into a list of words.
"""


def text_tokenize(text, alpha_token=False, word_len=None, stop_words=None, stemmer=None):
    # Define the punctuation translator
    translator = str.maketrans('', '', string.punctuation)
    # Tokenize sentence into words
    words = nltk.word_tokenize(text)
    # Basic cleaning: lower case, punctuations and nulls removed
    words = [word.lower() for word in words]
    words = [word.translate(translator) for word in words]
    words = [word for word in words if word != '']

    # If needed: length filter, non-alphabetic words, removing stopwords, stemming
    if alpha_token:
        words = [word for word in words if word.isalpha()]
    if word_len:
        words = [word for word in words if word_len[0] <= len(word) <= word_len[1]]
    if stop_words:
        words = [word for word in words if word not in stop_words]
    if stemmer:
        words = [stemmer.stem(word) for word in words]

    # Return the list of processed words
    return words


# %% Main Function:
"""
The function WaybackScraper() serves as the main function of the program.
It generate bag of words for a time-series of company websites.
"""


def WaybackScraper(host,
                   freq,
                   date_range=None,
                   max_url=MAX_URL,
                   max_sub=MAX_SUB,
                   bow_options=BOW_OPTIONS,
                   path=PATH):

    # Search all archives for the entered URL
    df = wayback_query(host)

    # Break if no result found
    if df is None:
        return

    # Store the API query results
    df.to_csv(path+'cdx['+re.sub(r'[^\w\s\-]', '_', host)+'].csv', index=False)

    # Aggregate query results at desired frequency
    df = query_filter(df, freq, date_range)

    # Scrape all URLs and their subs
    url_res_all = {}
    for url in df['url'].values:
        tree_res = tree_scrape(url, max_url, max_sub)
        url_res_all[url] = tree_res

    # Store the time-series of scraped results
    with open(path+'res['+re.sub(r'[^\w\s\-]', '_', host)+'].json', 'w') as f:
        json.dump(url_res_all, f)

    # Process scraped html texts
    args = bow_options.values()
    url_bow_all = {url: Counter(itertools.chain(*[text_tokenize(url_res['text'], *args) for url_res in tree_res]))
                   for url, tree_res in url_res_all.items()}

    # Store the time-series of formed BoWs
    with open(path+'bow[' + re.sub(r'[^\w\s\-]', '_', host)+'].json', 'w') as f:
        json.dump(url_bow_all, f)


if __name__ == "__main__":
    """
    To pass function arguments from command line, uncomment this code block
    host = sys.argv[1]
    freq = sys.argv[2]
    date_range = (sys.argv[3], sys.argv[4])
    WaybackScraper(host=host,
                   freq=freq,
                   date_range=date_range)
    """
    WaybackScraper(host='www.bp.com',
                   freq='Q',
                   date_range=('2008/01/01', '2014/12/31'))
