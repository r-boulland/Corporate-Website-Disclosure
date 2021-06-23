# Corporate Websites: A New Measure of Voluntary Disclosure
*Romain Boulland, Thomas Bourveau, Matthias Breuer*

<hr>
This repository contains the data and code needed to replicate the main findings of Boulland, Bourveau, and Breuer (2021): "Corporate Websites: A New Measure of Voluntary Disclosure" (<a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3816623">SSRN link</a>). 
The first section details the steps to: i) extract data from the Wayback Machine Application Programming Interface (API) ; and ii) construct the website-based measure of disclosure. The code provided can be easily tailored to construct the measure for firms outside the sample studied in Boulland, Bourveau, Breuer (2021). The second section provides the code and data to study the relationship between the website-based measure of disclosure and liquidity for firms in the CRSP-Compustat universe.


## Construction of the measure.
It contains the following file:

- **example_wayback.json**: the Wayback machine JSON extract for one firm;
- **json_to_csv.py**: a JSON to CSV converter;
- **construct_measure.do**: A do-file detailing the steps to construct the quarterly website-based measure of disclosure (`size_website_q`).


Wayback Machine data are extracted by querying the API using the following command:**http://web.archive.org/cdx/search/cdx?url=www.cecoenviro.com&matchtype=domain&collapse=timestamp:10&matchType=prefix&output=json**. In this command, the field **url** should point to the corporate website. To collect the data on a sample of firms, there are several possibilities. One that is easy to implement is to use the GNU **wget** program which is available as a command line in MacOS, Microsoft Windows (PowerShell), or Linux. The **wget** command accepts as an argument a file listing the URLs to be downloaded. See the GNU wget documentation for more details.
The resulting file is a JSON file (**example_wayback.json**). Because Stata does not read natively JSON files, it is necessary to translate them into CSV files. This can be done using the **json_to_csv.py** parser.
Finally,**construct_measure.do** is a do-file which takes as an input the CSV file and build the website-based measure of disclosure at the quarterly level.

## Relationship between the website-based measure of disclosure and firm liquidity (CRSP-Compustat universe).

- **corporate_website_disclosure.dta**: A STATA dataset containing our website-based measure of disclosure at the quarterly level. The dataset contains the following variables:
  - `gvkey`: The gvkey identifier of the firm;
  - `id`: A unique firm identifier in numeric format;
  - `q`: the quarter during which the size of the corporate website was measured;
  - `size_website_q`: the size of the website (in Bytes) that quarter;
  - `size_mim_text`: the size of the text elements of the website corresponding to the mimetype 'text/html';
  - `sector_gind`: the four-digit GICS code to which the firm belongs.

- **replication_Website_Disclosure.do**. A do-file detailing the steps to replicate the main results of the paper.



To replicate the results, you will need access to the following commercial datasets:
- **crsp_msf**: daily stock price data from the Center for Research in Security Price (CRSP);
- **link_table**: the historical gvkey-permno mapping from the CRSP-Compustat Merged Database, maintained by Wharton Research Data Services (WRDS).

