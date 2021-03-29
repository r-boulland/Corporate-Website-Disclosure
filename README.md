# Corporate Websites: A New Measure of Voluntary Disclosure
*Romain Boulland, Thomas Bourveau, Matthias Breuer*

<hr>
This repository contains the data and code needed to replicate the main findings of Boulland, Bourveau, and Breuer (2021): "Corporate Websites: A New Measure of Voluntary Disclosure". It contains the following elements:


- corporate_website_disclosure.csv: A dataset containing our website-based measure of disclosure at the quarterly level. The dataset contains the following variables:
  - gvkey: The gvkey identifier of the firm;
  - id: A unique firm identifier in numeric format;
  - q: the quarter during which the size of the corporate website was measured;
  - size_website_q: the size of the website (in Bytes) that quarter;
  - size_mim_X: a serie of variables indicating the size of each element of the website (X='video','audio','image','text','application','other');
  - group_gind: the four-digit GICS code to which the firm belongs.

- replication_BBB.do. A STATA do-file detailing the steps to replicate the main results of the paper.



To replicate the results, you will need access to the following proprietary datasets:
- crsp_msf: daily stock price data from the Center for Research in Security Price (CRSP);
- link_table: the historical gvkey-permno mapping from the CRSP-Compustat Merged Database (from the Wharton Research Data Services).

