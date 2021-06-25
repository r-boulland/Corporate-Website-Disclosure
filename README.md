# Corporate Websites: A New Measure of Voluntary Disclosure
*Romain Boulland, Thomas Bourveau, Matthias Breuer*

<hr>
This repository contains the data and code needed to replicate the main findings of Boulland, Bourveau, and Breuer (2021): "Corporate Websites: A New Measure of Voluntary Disclosure" (<a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3816623">SSRN link</a>). 
The first section details the steps to: i) extract data from the Wayback Machine Application Programming Interface (API) ; and ii) construct the website-based measure of disclosure. The second section provides the code to parse corporate websites' content using a bag-of-word representation. In both sections, the code can be tailored to construct the measure for firms outside the sample studied in Boulland, Bourveau, Breuer (2021). The third section provides the code and data to study the relationship between the website-based measure of disclosure and liquidity for firms in the CRSP-Compustat universe.


## Construction of the measure
It contains the following files:

- **[example_wayback.json](example_wayback.json)**: the Wayback machine JSON extract for one firm;
- **[json_to_csv.py](json_to_csv.py)**: a JSON to CSV converter;
- **[construct_measure.do](construct_measure.do)**: A do-file detailing the steps to construct the quarterly website-based measure of disclosure (`size_website_q`).


Wayback Machine data are extracted by querying the API using the following call (**api_call**):
**http://web.archive.org/cdx/search/cdx?url=www.cecoenviro.com&matchtype=domain&collapse=timestamp:10&matchType=prefix&output=json**. 

In this command, the field **url** should point to the corporate website. To collect the data on a sample of firms, there are several possibilities, among which:
- the GNU **wget** program which is available as a command line in MacOS, Linux, or Microsoft Windows (PowerShell). The general syntax is **wget api_call**. The command also accepts a list of files as an argument, which allows for batch downloading. See the wget documentation for more details; 
- the **copy** command in STATA, which allows to copy an URL to a file. The syntax is **copy api_call *outputfile***;
- a download manager which allows for batch downloading (*Free Download Manager* for instance is a good open-source option).

The resulting file is a JSON file (**[example_wayback.json](example_wayback.json)**). Because Stata does not read native JSON files, it is necessary to translate them into CSV files. This can be done using the **[json_to_csv.py](json_to_csv.py)** parser.

Finally, **[construct_measure.do](construct_measure.do)** is a do-file which takes as an input the CSV file and builds the website-based measure of disclosure at the quarterly level.

## Parsing corporate websites

The program **[WaybackScraper.py](website_scraping/WaybackScraper.py)** scrapes a time-series of archived company webpages stored on the Wayback Machine. It provides a representation of their textual contents using a bag-of-words approach. Please check dependency and customize the **[config.py](website_scraping/config.py)** file before launching the program.

**Main Parameters** (**[WaybackScraper.py](website_scraping/WaybackScraper.py)**)
- ***host***:*str* Host URL for a given company;
- ***freq***: *DateOffset, Timedelta, or str* Frequency at which the sent URL is scraped. For more information on offset aliases, see [here](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases);
- ***date_range***: *(str,str),default None* Date (yyyy/mm/dd) range of URL search.

**Program configuration** (**[config.py](website_scraping/config.py)**)
- ***path***: *str, default ‘./’* Path to store all outputs;
- ***max_url***: *int, default 10* The maximum number of URLs to scrape within the tree of a given root URL;
- ***max_sub***: *int default 1* The maximum level of sub-URLs to scrape within the tree of a given root URL;
- ***alpha_token***: *bool, default True* Boolean variable indicating whether consider alphabetic tokens exclusively or not;
- ***word_len***: *(int, int), default (1, 20)* Length range of accepted tokens;
- ***stop_words***: *list, default nltk.corpus.stopwords.words(‘english’)* A list of stopwords escaped during tokenization;
- ***stemmer***: *nltk.stem.api.StemmerI, default nltk.stem.porter.PorterStemmer()* A stemmer object to stem tokenized words. 
- ***status_code***: *[str, …], default [‘200’]* A list of HTTP status code allowed. For more information on HTTP status code, check [here](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes);
- ***mime_type***: *[str, …], default [‘text/html’]* A list of MIME types allowed. For more information on MIME types, check [here](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types);
- ***header***: *dict, default {}* Headers when requesting a URL when request();
- ***parser***: *str, default ‘lxml’* The parser used to parse scraped HTMLs;
- ***raw***: *bool, default False* Boolean variable indicating whether store the raw HTML text or not.

## Relationship between the website-based measure of disclosure and firm liquidity (CRSP-Compustat universe)

- **[corporate_website_disclosure.dta](corporate_website_disclosure.dta)**: A STATA dataset containing the website-based measure of disclosure at the quarterly level. The dataset contains the following variables:
  - `gvkey`: The gvkey identifier of the firm;
  - `id`: A unique firm identifier in numeric format;
  - `q`: the quarter during which the size of the corporate website was measured;
  - `size_website_q`: the size of the website (in Bytes) that quarter;
  - `size_mim_text`: the size of the text elements of the website corresponding to the mimetype 'text/html';
  - `sector_gind`: the four-digit GICS code to which the firm belongs.

- **[replication_Website_Disclosure.do](replication_Website_Disclosure.do)**. A do-file detailing the steps to replicate the main results of the paper.



To replicate the results, you will need access to the following commercial datasets:
- **crsp_msf**: daily stock price data from the Center for Research in Security Price (CRSP);
- **link_table**: the historical gvkey-permno mapping from the CRSP-Compustat Merged Database, maintained by Wharton Research Data Services (WRDS).

