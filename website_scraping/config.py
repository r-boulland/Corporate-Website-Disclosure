#!/apps/anaconda3/bin/python3
"""
Author: Romain Boulland, Thomas Bourveau, Matthias Breuer
Date: Jun 24, 2021
Code: Configurations of the program WaybackScraper()
"""


# %% Packages
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from fake_headers import Headers

# %% Configs
contact = 'youremail@domain.com'
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '\
            'AppleWebKit/537.36n(KHTML, like Gecko) '\
            'Chrome/80.0.3987.116 Safari / 537.36'
headers = {'User-Agent': useragent, 'From': contact}
parser = 'lxml'
raw = False
status_code = ['200']
mime_type = ['text/html']

max_url = 10
max_sub = 1

"""
alpha_token = False
word_len = None
stop_words = None
stemmer = None
"""
alpha_token = True
word_len = (1, 20)
stop_words = stopwords.words('english')
stemmer = PorterStemmer()
bow_options = {'alpha_token': alpha_token, 'word_len': word_len, 'stop_words': stop_words, 'stemmer': stemmer}

path = './'
