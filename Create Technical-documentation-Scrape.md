# Technical documentation for use of Python module Scrape

This document is a documentation file for the Python module **Scrape.py**. The module is comprised by 6 functions, of these 3 are auxiliary. The functions are used for scraping job portal pages on the http://www.jobportal.com domain. The functions represent a crawler and scraper that open a web browser, which runs JavaScript and are not detected as robots. Note: a Mozilla Firefox installation and a geckodriver executable are needed. More details in the _scrape_linklist program description.
The scraping process runs in three steps:

*	the crawler connects to the subpage that lists job vacancy, collects their internet address into a list of job vacancies,
*	the crawler finds the next page, connects to it and repeats the above step,
*	scraper agents are run over the list of addresses and collect the information.

Scrapers run in multithread mode on 3 threads. This is because we have an agreement with job portals to only use three agents at once. A working log is written at the same time.
This module imports other modules and outside functions to work correctly:
*	function *BeautifulSoup* (from module **bs4**)
*	function *webdriver* (from module **selenium**)
*	function *Options* (from module **selenium.webdriver.firefox.options**)
*	function *FirefoxBinary* (from module **selenium.webdriver.firefox.firefox_binary**)
*	function *TimeoutException* (from module **selenium.common.exceptions**)
*	function *url* (from module **urllib.request**)
*	module **time**
*	function *datetime* (from module **datetime**)
*	module **csv**
*	module **sys**
*	module **os**
*	module **re**
*	functions *Process* and *Queue* (from module **multiprocessing**)
*	module **signal**

***NOTE:** This module requires the Firefox webdriver geckodriver, available at https://github.com/mozilla/geckodriver.*



## Main functions in the module:
### *PP_scrape_linklist*: 
a program that scrapes all webpages in a list. The list is split into 3 parts, which are then fed scraper agents at once. Every agent may produce a working log, which are then merged together at the end of the job. If the program does not fail, the agent logs are deleted. At the end any remainder of the links is checked. The identification in the log files for this agent is the character "$".The output of the program is a list with job vacancies data. Uses _scrape_linklist and _qscrape_linklist auxiliary programs!
The parameters are:

1.	JVs – list of job vacancy subpages on the job portal (type list of strings),
2.	options – options for the geckodriver browser (type list of strings),
3.	sleeptime – time to wait between each step in the loop of scraping (type integer),
4.	to_log – full path to the chosen address where the log will be created (type string); if False or empty string then no log will be created.

The output of the function is:

5.	results – a table (list of lists of strings) where each row corresponds to a job vacancy on the domain, columns are job vacancies’ characteristics as defined in the _scrape_linklist program.



### scrape_moje_delo:
the main program for scraping job vacancies from http://www.jobportal.com. After inputting the initial subpage with vacancies listed, it crawls over all next pages and collects each vacancy’s subpage and scrapes it. Crawling is executed in.-code and via the auxiliary program _find_next_page, scraping is executed by the PP_scrape_linklist program. The program’s outputs are a scraped vacancies, detected vacancies, failed vacancies, and time elapsed. A log of all the work may be written.
The parameters (all optional) are:

1.	*webaddress* – the initial webpage whit the start of the list of job vacancies (type string); the default page is "https://www.jobportal.com/link-to-first-page-of-job-list", the first page of all job vacancies on http://www.jobportal.com,
2.	*options* – geckodriver’s options (type string or list of strings); the default is "—headless", which makes the geckodriver browser run in headless mode, 
3.	*sleeptime* – time to wait between each step in the loop of scraping (type integer),
4.	*to_log* – the full path of the map where the log should be created (type string); the default is an empty string, which doesn’t produce a log.

The outputs of the function are:

5.	scrap – collected data on job vacancies (type list of lists of strings),
6.	boxes – a list of all vacancy box items vacancies on the internet domain (type  list of lists of strings) with time and date of connection and scraping,
7.	failed_JVs – a list of items that failed at scraping (type list of strings)
8.	time_elapsed – total elapsed from the start to the finish of the execution (type integer).



### scrape_sites:
a program that takes a table of scraped information, a list of scraped websites with time and date, a list of failed links to be scraped again and time elapsed from previous processes that edits all data into the final output table with scraped observations of job vacancies. The inputs should have the same format as the outputs of the scrape_job_portal program.  The output can be saved to a csv file. A log of all the work may be written.
The parameters are (optional parameter in italics):

1.	scrap – collected data on job vacancies (type list of lists of strings),
2.	boxes – a list of all vacancy box items vacancies on the domain (type  list of lists of strings) with time and date of connection and scraping,
3.	failed_JVs – a list of items that failed at scraping (type list of strings)
4.	time_elapsed – total elapsed from the start to the finish of the execution (type integer).
5.	*options*  – geckodriver’s options (type string or list of strings); the default is “—headless”, which makes the geckodriver browser run in headless mode, 
6.	*sleeptime* – time to wait between each step in the loop of scraping (type integer),
7.	*to_csv* – the full path of the map where a csv file with the final result can be created (type string); the default is an empty string, which does not produce the file.
8.	*to_log* – the full path of the map where the log should be created (type string); the default is an empty string, which does not produce a log.

The output of the function is:

9.	boxes – a table with job vacancies as observations and their data as columns (type list of lists of strings).
The variables in the output are:
    *	VacancyPost – the name of the job vacancy,
    *	LinkToJV – the internet address of the subpage with the vacancy’s post,
    *	ScrapeDate – the date of scraping,
    *	ScrapeTime – the time of scraping,
    *	PostDate – the date of the publication of the job vacancy on the portal,
    *	Firm – the enterprise that published the vacancy,
    *	VacancySite – the location (town, city, or region) where the vacancy is open,
    *	Sex – the gender of the desirable employee,
    *	SourceLink – the actual internet address of the vacancy post (in case of redirects),
    *	Content – the unstructured part of the post.



## Auxiliary functions in the module:
### _find_next_page:
a program that finds the link to the next page of the list of job vacancy posts on the domain. It searches through the HTML to find a "pagination" or "PagedList-Next" class in the tags, or a link with the title "next page".
The parameter: 
1.	soup – the HTML code, processed with BeautifulSoup (type string)

The output of this function is:

2.	next_page – the link to the next page (type string)



### _scrape_linklist:
a program that opens a browser and scrapes the contents of the links in the first input. This is the program that is executed in each thread by the PP_scrape_linklist program. The identification of each scraper agent and its work is recorded in the log (if it is written).
The parameters are:

1.	lst – list of web addresses to be scraped (type list of strings),
2.	options – geckodriver’s options (type string or list of strings), 
3.	sleeptime – time to wait between each step in the loop of scraping (type integer),
4.	th – the identification number of the scrape agent (type integer),
5.	to_log - the full path of the map where the log should be created (type string); if empty string or  False, does not produce a log.

The output of this function is:

6.	jobs – a list with a web address, actual internet address of the vacancy post and its content as an item, for each link in the lst. This is used to fill the observations of PP_scrape_linklist outputs.

***Note:** this program uses a Firefox simulation browser, and for it to work, the user has to have a Mozilla Firefox installed and a geckodriver executable on their machine. __We highly recommend__ that the Mozilla Firefox version is 61.0.2 (Firefox Quantum) and the geckodriver version is 0.20.1 as this is used in our office. Both of these programs were tested on Windows and Linux systems on this versions. To stop Firefox from automatically updating select the “Never check for updates (not recommended)” option in Firefox Options AND search and deselect the option “app.update.auto” on the “about:config” page of Firefox (Firefox configuration editor).*



### _qscrape_linklist:
prepares an individual _scrape_linklist program for multithread processing, putting it into a Queue. This is done get the multiprocessing module to work correctly.
The parameters are:

1.	queue – the Queue, into which the _scrape_linklist program is wrapped (type multiprocessing.Queue),
2.	lst – list of web addresses to be scraped (type list of strings),
3.	options – geckodriver’s options (type string or list of strings), 
4.	sleeptime – time to wait between each step in the loop of scraping (type integer),
5.	th – the identification number of the scrape agent (type integer),
6.	to_log - the full path of the map where the log should be created (type string); if empty string or  False, does not produce a log.

The output of this function is:

7.	A queued output from the _scrape_linklist program.
