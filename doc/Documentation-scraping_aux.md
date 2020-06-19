# Technical documentation for Slovenian scraping robots - the _scraping_aux_ file
This document describes the module _scraping_aux_, which is used to store some common auxiliary functions to help in scraping with the 
_Driver_ and _Scraper_ objects. The module runs in Python version 3.5 or higher. 

It includes five functions and a scripting functionality that enables scheduled scraping. The functions require the following modules 
and methods to work:
 * module csv,
 * module sys,
 * module os,
 * FirefoxWebElement (from module selenium.webdriver.firefox.webelement),
 * WebElement (from module selenium.webdriver.remote.webelement),
 * datetime, timedelta (from module datetime),
 * sleep (from module time),
 * StaleElementReferenceException (from module selenium.common.exceptions),
 * module win_unicode_console
 
## Auxiliary functions
The functions in this module are used across all scraping functions (in the _domain_tag_ scripts). They are not bound by any prescribed 
inputs or outputs and are entirely to the user what and how they work. We include some of the more useful functions, that are used for
our scraping needs. To see how a function is called from this module into a scraping file, see the code and documentation for 
_domain_tag_.

### `check_previous_links(domain_name, archive_dir, other_chs=None)`
This function stores any URL addresses found in the first column of .csv files in the _archive_dir_ that have the _domain_name_ in 
their name. This is used to exclude already scraped links from being scraped again and thus consume both yours and the URL domain's 
time and bandwitch. The optional parameter _other_chs_ is used to include only files with a specific substring in their name. If left 
`None`, this parameter is ignored.

### `schedule_scraping(module, dateandtime="")`
This function is used to schedule a scraping file for some time in the future. The parameter _module_ selects which scraping file is 
executed by file name, while _dateandtime_ selects the date and time to start the scraping. \
In the specific, the _schedule_scraping_ first loads the scraping file, then waits for the date and time specified and lastly calls the 
`module.main()` function. The waiting interval used while waiting is of 1 second. If the parameter _dateandtime_ is left empty, the 
scraping is executed immediately. The format of the _dateandtime_ parameter is: **dd.mm.yyyy/hh:mm** \
For the function to work correctly, the system must be set to the directory of the scraping file. If the name of the scraping file is 
not recognized, an error is raised. For more information see the **_NOTE_** at the end of this document.

### `send_buttons(driver_, xpath, keys=None, pos=0)`
This function is used to interact with a dynamic page loaded on the _driver_ object. The exact part of the page that is interacted with
is selected by the _xpath_ value, which can be the actual element's [XPath](https://en.wikipedia.org/wiki/XPath) string or a [Selenium 
WebDriver element](https://selenium-python.readthedocs.io/locating-elements.html). \
[Keys](https://selenium-python.readthedocs.io/getting-started.html) or strings can be passed with the parameter _keys_. If _keys_ is
left `None`, then an ordinary left mouse-button press is executed. If multiple elements use the same XPath, _pos_ can be used to choose
the desired element by order (**note:** don't forget Python ordering starts with 0).

**_NOTE:_** this function is executed using JavaScript which is not supported on every page. Selenium also includes a method of pressing
and/or passing keys to elements which does not require JavaScript, but it does require that the element is available for interaction. 
This means it's must be visible in the browser, on top of other elements and enabled. \
Both methods of executing pressing are valid and each is used in different scenarios.

### `numbers_report(lst, save_dir, date_format=%d.%m.%Y")`
This function writes the basic statistic of items in the list _lst_ to the file _save_dir_. It's used to monitor the number of items
found while scraping. Each scraping period is finished by recording the number of items in the scraping output matched with the scraping
date. By default the time format is __dd.mm.yyyy__, but this can be changed with the _date_format_ parameter.

Since internet sites are mostly unstable, this way we can notice when something unexpected happened to the pages, even if scraping 
completed successfully. We recommend to our user to use this function and monitor their outputs if projects require extended scraping of
the same pages through time.

### `next_monday(date, day=0)`
This practical function returns the datetime object of the first next monday after the input _date_. Keep in mind that _date_ must be a
Python [datetime](https://docs.python.org/3/library/datetime.html) object. By changing the value of _day_ the function returns any other
day in the week as well. The value of _day_ can be any integer, however the function will always return the date of a day in the next 7
days of _date_. If the value is negative, the days will follow backwards (-1 is sunday, -2 is saturday etc.).

## The script mechanic
If this file is called by command 
```
python -m scraping_aux _module_ _dateandtime_
```
where _\_module\__ and _\_date_and_time_\_ are arguments used as in the _schedule_scraping_ function, then the respective scraping 
function executes at the specified time (this must be `""`˙if an instantaneous start is preferred).
________________________________________________
**_NOTE:_** \
keep in mind that the computer needs to know where Python, _scraping_aux.py_ and the scraping file are located for the 
function _schedule_scraping_ (and consequently for the scripting mechanic) to work correctly. Usually the Python path is automatically
saved in the environmental variables, and we would advise to store the scraping modules there as well. \
However, if the paths are not saved in the environmental variables (e.g. no administrative privilege at Python installation), the 
programmes can still be used, but the full version of the above command is more complicated. The below code works on Linux:
```
cd /path/to/the/module/file
/path/to/python3 /path/to/scraping_aux.py module_file dateandtime
```
If the system you scrape on is Windows an additional middle line needs to be added with specification to the Drive. In the example below
the Drives used are X, Y, and Z:
```
cd X:\path\to\the\module\file
X:
Y:\path\to\python3 Z:\path\to\scraping_aux.py module_file dateandtime
```
Also remember, that any spaces in folder or file names break the commands, and in such cases you have to quote (`""`) their paths.
