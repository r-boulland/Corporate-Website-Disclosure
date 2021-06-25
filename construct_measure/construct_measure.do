*-------------------------------
* Utility Programs 
*-------------------------------

*Format date
capture program drop datewb
program def datewb
	format timestamp %16.0g
	capture tostring timestamp,replace usedisplayformat  
	gen date=date(substr(timestamp,1,4)+substr(timestamp,5,2)+substr(timestamp,7,2),"YMD")
	format date %td
end
*Format statuscode
capture program drop statuscode
program def statuscode
	format statuscode %9s
	tostring statuscode,replace usedisplayformat
	gen code=substr(statuscode,1,1)
end

*--------------------------------------
* Website-based measure of disclosure
*-------------------------------------

capture program drop wayback
program define wayback
	insheet using "`1'",clear
	*-------------------------
	* get the website name
	*---------------------------
	gen t=urlkey[1]
	gen str website= regexs(2)+"."+regexs(1)  if regexm(t, "(.*),(.*)\)")
	drop t
	*-------------------------
	* Processing date and errors
	*---------------------------
	*Date
	datewb
	gen q=qofd(date)
	format q %tq
	gen y=year(date)
	drop timestamp
	*Remove errors
	statuscode
	drop if code=="3"|code=="4"
	drop code statuscode
	*Define length
	capture destring length,replace
	*-------------------------
	* Compute website size
	*---------------------------
	*first, compute the average size of each URL per quarter
	bys urlkey q:egen size_url_q=mean(length)
	*second, keep one url per quarter
	bys q urlkey:keep if _n==1
	*Finally, compute website size as the sum of each URL average length
	bys q:egen size_website_q=sum(size_url_q)
	*------------------------------
	*Keep relevant variables and save the dataset
	*-----------------------------
	bys q:keep if _n==1
	keep website q size_website_q
	save "`2'",replace
end
exit

*--------------------------------------
* Call the program
*-------------------------------------
* Construct the measure for one firm
global input "C:\Users\Boulland\csv\example_wayback.csv"
global output "C:\Users\Boulland\example_disclosure.dta"

wayback "$input" "$output"

