/********************************************************************************************/
/* Paper: "Corporate Websites: A New Measure of Voluntary Disclosure"						*/
/* Program:	Generate the main results of the paper     										*/
/* Authors: Romain Boulland (ESSEC); Thomas Bourveau (Columbia); Matthias Breuer (Columbia)	*/
/* Input datasets: crsp_dsf; link_table; corporate_website_disclosure.dta			  											*/
/********************************************************************************************/

version 14.2
clear all
set more off

* Directory of the project
global directory = "C:\xxxxx\xxxxx"

* Set up the working directory in the subfolder where the three input datasets are located
cd "$directory\Data"

* Output directories
global table="$directory\tables"
global fig="$directory\figures"

* Directory to store temporary files
global temp = "C:\data"



/**************************************************************************************/
/*Step 1- Compute the liquidity measures using: i) link_table; and ii) crsp_dsf     ***/
/**************************************************************************************/

/******************************************************************************/
/* Prepare the link table between Permno and Gvkey							  */
/******************************************************************************/
use link_table, clear
keep lpermno gvkey linktype linkprim linkdt linkenddt weburl  
save "$temp/link", replace

/******************************************************************************/
/* Calculate liquidity measures on the merged CRSP-Compustat dataset 		  */
/******************************************************************************/
/* Daily stock file */
use crsp_dsf, clear
keep if shrcd == 10 | shrcd == 11
rename permno lpermno
/* Link table CRSP-COMPUSTAT */
	/* Joinby */
	joinby lpermno using "$temp/link"
	/* Link type */
	keep if linktype == "LU" | linktype == "LC"
	/* Primary link */
	keep if linkprim == "P" | linkprim == "C"
	/* Date range */
	keep if linkdt <= date & date <= linkenddt
/* Quarter */
gen q = qofd(date)
format q %tq
/* Adjustments */
	/* Returns */
	replace ret = . if abs(ret) > 1
/* Bid-ask spread */
	gen spread = (ask - bid)/(0.5*(bid + ask))
	/* Market cap */
	gen mkcap = abs(prc) * shrout
	/* Share turnover */
	gen dvol = (prc * vol) / (prc * shrout * 1000)
/* Panel */
	xtset lpermno date
/* Quarter aggregation */
	/* Collapse */
	collapse (median) spread (mean) dvol (sd) ret (lastnm) mkcap lpermno weburl, by(gvkey q) fast
/* take variables 4 quarters prior*/
	sort gvkey q
	by gvkey:g mkcap_lag=mkcap[_n-4] if q==q[_n-4]+4
	by gvkey:g dvol_lag=dvol[_n-4] if q==q[_n-4]+4
	by gvkey:g sdret_lag=ret[_n-4] if q==q[_n-4]+4
	/* Save */
save "$temp/liquidity", replace



/****************************************************************************************/
/*Step 2- Merge the website-based measure with liquidity measures and run the analysis   */
/* using : i) corporate_website_disclosure; and ii) liquidity.dta (from Step 1). 						*/
/****************************************************************************************/

/*Open the website-based measure of disclosure and merge it with liquidity*/
use corporate_website_disclosure,clear
*Merge with capital market variables
merge 1:1 gvkey q using "$temp/liquidity",keep(3) nogen

/*trim dependent and independent variables*/
local variables= "spread mkcap_lag dvol_lag sdret_lag size_website_q"
foreach y of local variables {
	qui sum `y', d
	qui replace `y' = . if r(p1) > `y' | r(p99) < `y'
}

/* Log-transformation of the dependent variable */
gen ln_spread=ln(spread)

/*log-transformation of the disclosure variable*/
gen ln_size_website_q=ln(size_website_q)


/* Log-transformation of control variables*/
gen ln_mkcap_lag=ln(mkcap_lag)
gen ln_dvol_lag=ln(dvol_lag)
gen ln_sdret_lag=ln(sdret_lag)

/*scale the disclosure variable for readibility purpose*/
replace ln_size_website_q=ln_size_website_q/10

/*Set up parameters for the regressions*/
est clear
gen a=1
local cluster = "id"
local controls="ln_mkcap_lag ln_dvol_lag ln_sdret_lag "
local a="a"
local FE1="q"
local FE2="sector_gind"
local FE3="id"
local table_name="Table_3"

/*Set up parameters for the output tables*/
capture rm "$table/`table_name'.xls"
capture rm "$table/`table_name'.txt"
local option="excel alpha(0.01, 0.05, 0.1) symbol(***, **, *) dec(3) label e(r2 r2_a r2_within r2_a_within) "

/*Take the same sample accross all specifications*/
reghdfe ln_spread ln_size_website_q `controls',absorb(`FE1' `FE3') vce(cluster `cluster')
gen e=e(sample)

/*Run regressions (Table 3), sleep for 1+ second between each regression to make sure the output table closes properly*/
reghdfe ln_spread ln_size_website_q if e==1,absorb(`a') vce(cluster `cluster')
outreg2 using "$table/`table_name'.xls",append addtext(Year-Quarter FE, NO,Industry FE,NO, Firm FE,NO,Cluster,`cluster') `option' 
sleep 1000

reghdfe ln_spread ln_size_website_q `controls' if e==1,absorb(`a') vce(cluster `cluster')
outreg2 using "$table/`table_name'.xls",append addtext(Year-Quarter FE, NO,Industry FE,NO, Firm FE,NO,Cluster,`cluster') `option'
sleep 1000

reghdfe ln_spread ln_size_website_q `controls' if e==1,absorb(`FE1') vce(cluster `cluster')
outreg2 using "$table/`table_name'.xls",append addtext(Year-Quarter FE, YES,Industry FE,NO, Firm FE,NO,Cluster,`cluster') `option'
sleep 1000

reghdfe ln_spread ln_size_website_q `controls' if e==1,absorb(`FE1' `FE2') vce(cluster `cluster')
outreg2 using "$table/`table_name'.xls",append addtext(Year-Quarter FE, YES,Industry FE,YES, Firm FE,NO,Cluster,`cluster') `option'
sleep 1000

reghdfe ln_spread ln_size_website_q `controls' if e==1,absorb(`FE1' `FE3') vce(cluster `cluster')
outreg2 using "$table/`table_name'.xls",append addtext(Year-Quarter FE, YES,Industry FE,NO, Firm FE,YES,Cluster,`cluster') `option'
sleep 1000

*keep this dataset for later use
save "$temp/regression_wayback",replace

/****************************************************************************************************************/
/* Robustness: regression of Bid-Ask spread on Website Size, text element only*/
/****************************************************************************************************************/
use "$temp/regression_wayback",clear
drop e a

/*log transformation of the disclosure variable based on text*/
gen ln_size_mim_text_q=ln(size_mim_text_q)

/*scale some variables for readibility purpose*/
replace ln_size_mim_text_q=ln_size_mim_text_q/10

/*constant for the baseline model*/
gen a=1

est clear
local cluster = "id"
local controls="ln_mkcap_lag ln_dvol_lag ln_sdret_lag "
local a="a"
local FE1="q"
local FE2="sector_gind"
local FE3="id"
local table_name="Table_3_text_only"


capture rm "$table/`table_name'.xls"
capture rm "$table/`table_name'.txt"

local option="excel alpha(0.01, 0.05, 0.1) symbol(***, **, *) dec(3) label e(r2 r2_a r2_within r2_a_within) "

*Make sure we are working on the exact same sample as in Table 3  
reghdfe ln_spread ln_size_website_q `controls',absorb(`FE1' `FE3') vce(cluster `cluster')
gen e=e(sample)
*In a few cases (2,395 observations), the total size of text elements is missing, and all elements are classified as "Other". Probably because the websites use non-HTML text elements. We assume in that case that other=text.  Minimal impact, only the #obs is affected.    
replace ln_size_mim_text_q =ln_size_website_q if ln_size_mim_text_q ==. & e==1

/*Run regressions (Table 3)*/
reghdfe ln_spread ln_size_mim_text_q if e==1,absorb(`a') vce(cluster `cluster')
outreg2 using "$table/`table_name'.xls",append addtext(Year-Quarter FE, NO,Industry FE,NO, Firm FE,NO,Cluster,`cluster') `option' 
sleep 1000

reghdfe ln_spread ln_size_mim_text_q `controls' if e==1,absorb(`a') vce(cluster `cluster')
outreg2 using "$table/`table_name'.xls",append addtext(Year-Quarter FE, NO,Industry FE,NO, Firm FE,NO,Cluster,`cluster') `option'
sleep 1000

reghdfe ln_spread ln_size_mim_text_q `controls' if e==1,absorb(`FE1') vce(cluster `cluster')
outreg2 using "$table/`table_name'.xls",append addtext(Year-Quarter FE, YES,Industry FE,NO, Firm FE,NO,Cluster,`cluster') `option'
sleep 1000

reghdfe ln_spread ln_size_mim_text_q `controls' if e==1,absorb(`FE1' `FE2') vce(cluster `cluster')
outreg2 using "$table/`table_name'.xls",append addtext(Year-Quarter FE, YES,Industry FE,YES, Firm FE,NO,Cluster,`cluster') `option'
sleep 1000

reghdfe ln_spread ln_size_mim_text_q `controls' if e==1,absorb(`FE1' `FE3') vce(cluster `cluster')
outreg2 using "$table/`table_name'.xls",append addtext(Year-Quarter FE, YES,Industry FE,NO, Firm FE,YES,Cluster,`cluster') `option'
sleep 1000

/******************************************************************************/
/* Distribution of the measure (Figure 1)*/
/******************************************************************************/
use "$temp/regression_wayback",clear
gr tw hist ln_size_website_q  if mkcap<.,xtitle("ln(Website Size)") ytitle("") legend(off) saving("$fig/fig1_size",replace) graphregion(color(white)) plotregion(fcolor(white)) scheme(s2mono)
gr export "$table/fig1.png",replace

/************************************************************************************************/
/* Table 1 Panel A: Descriptive Statistics for the Wayback measure and capital-market variables */
/************************************************************************************************/
mat drop _all

*Website-based measure: the full sample (conditional *only* on non-missing Market Cap).
use "$temp/regression_wayback",clear
*scale back website size to have the size in Bytes
replace ln_size_website=ln_size_website*10
tabstat size_website_q ln_size_website if mkcap<.,stat(co me sd p25 p50 p75 ) columns(statistics) save
mat A1=r(StatTotal)'
mat rowname A1="Website Size (bytes)" "Website Size (log)"

*Capital-market variables: the reduced sample (conditional on non-missing observations for the spread+ the three control variables)
gen spread_pct=spread*100
replace mkcap_lag=mkcap_lag/1000
tabstat spread_pct mkcap_lag dvol_lag sdret_lag if e==1 ,stat(co me sd p25 p50 p75) columns(statistics) save
mat A2=r(StatTotal)'
mat rowname A2="Spread (in %)" "Market Value(t-4)" "Share Turnover(t-4)" "Return variability(t-4)"

mat A=A1\A2
mat lis A
putexcel set "$table/Table_1",sheet("Panel A") replace
putexcel A1 = matrix(A),names
mat drop _all


/****************************************************************************************************************/
/* Table 1 Panel D: Variance decomposition ***/
/****************************************************************************************************************/
*Take the full sample (all obs. with non-missing market cap).
use "$temp/regression_wayback",clear
keep if mkcap<.

mat A=.,.,.\.,.,.\.,.,.

local FE1="i.sector_gind"
local FE2="i.q"
local FE3="id"

xi:reg ln_size_website_q `FE1'
mat A[1,1]=e(r2)
xi:reg ln_size_website_q `FE2'
mat A[2,2]=e(r2)
xi:reg ln_size_website_q `FE1' `FE2'
mat A[2,1]=e(r2)
xi:areg ln_size_website_q,absorb(`FE3')
mat A[3,3]=e(r2)
xi:areg ln_size_website_q `FE2',absorb(`FE3')
mat A[3,2]=e(r2)

mat rownames A="Sector (GICS)" "Time" "Firm"
mat colnames A="GICS" "Time" "Firm"
putexcel set "$table/Table_1",sheet("Panel D") modify
putexcel A1 = matrix(A),names 



