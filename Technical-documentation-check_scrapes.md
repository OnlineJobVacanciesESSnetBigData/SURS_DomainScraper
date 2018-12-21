# Technical documentation for use of Python module check_scrapes

This document is a documentation file for the Python module **check_scrapes.py**. This module runs in Python 3.4 or above. The module is used to check the correctness of scraped data by the program **Run_Scrape.py**. The **check_scrapes.py** module is comprised by 1 function.
This module imports other modules and outside functions to work correctly:

1.	function *datetime* (from module **datetime**)
2.	function *windll* (from module **ctypes**)
3.	module **csv**
4.	module **sys**

## Main functions in the module:
### check_scrapes:
a program that checks the correctness of scraped data. The checks are performed on the following characteristics:
*	does the file exist,
*	does the file open correctly,
*	is the file filled at all,
*	is the first row composed by correct column names,
*	are the rows correct in length,
*	are the date formats of the columns "ScrapeDate" and "PostDate" correct,
*	is the time format of the column "ScrapeTime" correct,
*	is the columns "PostDate" in the correct column,
*	are there any redundant strings left in the columns (if they are common) .

The checks are performed on the files, that were created by the **Run_Scrape.py** program in the directory *\\PATH\\TO\\JOBPORTAL\\TABLE*.  The logs that may be updated should also be saved in this directory.
The parameters are (parameters in italics are optional):

1.	JP – job portal (string); the names must be the same as the start of the names of the files to be checked,
2.	*datum* – the date in the name of the file to be checked (type string of format "YEAR-mm-dd"); the default is date on the program running day,
3.	*to_log* – should the result be recorded to the log file (type string); the default is "".

The output of the function is:

4.	a Windows popup notification message with the status of the scraped data, listing errors.
5.	*possibly a new recording in the log of the original Scrape.py process.*
