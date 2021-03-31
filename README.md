# Corporate Websites: A New Measure of Voluntary Disclosure
*Romain Boulland, Thomas Bourveau, Matthias Breuer*

<hr>
This repository contains the data and code needed to replicate the main findings of Boulland, Bourveau, and Breuer (2021): "Corporate Websites: A New Measure of Voluntary Disclosure" (SSRN link). It contains the following STATA files:


- **corporate_website_disclosure.dta**: A dataset containing our website-based measure of disclosure at the quarterly level. The dataset contains the following variables:
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

