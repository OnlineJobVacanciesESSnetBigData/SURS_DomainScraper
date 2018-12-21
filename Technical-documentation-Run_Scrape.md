This document is a documentation file for the Python module **Run_Scrape.py**. This module runs in Python 3.4 or above. ***Note:** this process needs a Mozilla Firefox browser and a geckodriver executable. For more information check the document Scrape.doc.*

The **Run_Scrape.py** module is comprised by a set of rules, which run, edit, and save scraped data from the job board at the http://www.jobportal.com domain. The main work is done by the **Scrape.py** module.
This module imports other modules and outside functions to work correctly:
1.	custom functions *scrape_job_portal*, *scrape_sites* (from module **Scrape**)
2.	custom function *check_scrapes* (from module **check_scrapes**)
3.	functions *strftime*, *sleep* (from module **time**)
4.	module **sys**
5.	module **csv**

Additionally, the **Scrape.py** module uses Firefox’s geckodriver to connect to websites and run JavaScript. For more information, see documentation for the **Scrape.py** module (*Technical-documentation-Scrape.md*). The module only runs, when called as primary source (that is, if it is called into another module/program it will not run).
The module runs in four steps:
-	*scrape_job_portal* is run and its outputs are saved in memory, 
-	the starting website is http://www.jobportal.com/link-to-first-page-of-job-list,
-	*scrape_sites* is run after a delay of 30 seconds using previous outputs and the outputs are saved in memory,
-	rules, specific to the http://www.jobportal.com HTML structure, are applied to the output table of *scrape_sites*,
-	the table is saved to a CSV to a specific location. 
A checking process is applied on the output table via **check_scrapes.py** after two minutes of wait.
Changes to the scrape_sites output table:
-	all dates are changed to the DD.MM.YYY format; this should includes string elements, such as "Yesterday" and "Today" in the "PostDate" column,
-	content elements are cleaned,
-	content elements have newlines and tab characters replaced with spaces,
-	the first row with column names is added to the table.
