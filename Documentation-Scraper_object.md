# Technical documentation for Slovenian scraping robot - the Scraper object
This document describes the module _custom_scraper_, its main object _Scraper_ and their mechanics in detail. The module runs in Python 
version 3.5 or higher. The functions requires the following modules and methods to work:
 * Driver (from custom module custom_driver) and HTML parser _lxml_,
 * custom module scraping_aux (from module selenium),
 * module traceback,
 * module os,
 * module sys
 * module csv,
 * module time,
 * datetime (from module datetime),
 * Queue, Process and Manager (from module multiprocessing),
 * Empty (from module multiprocessing.queues),
 * WebDriverException (from module selenium.common.exceptions),
 * module win_unicode_console.

## Initialization
The object _Scraper_ is used to manage multiple instances of _Driver_ and their scraping processes. A _Scraper_ spawns a number of 
_Driver_ objects, opens the relevant page on each and then executes instructions from the _domain_tag_. 

First, a _Scraper_ object needs
to be initialized. During initialization, the _Scraper_ will check the Robots.txt document on the first input URL page (if not 
disabled). Then it will create a number of _Driver_ objects with the input attributes and found robots restrictions. If enabled, a 
logfile will be created. Each of the _Driver_ objects will write logs into separate files, that will be merged into the main one after 
finishing the scraping with log records sorted according to their timestamps.

The method _start_ can be used after initialization to actually begin the scraping process. The scraping is conducted according to the 
instructions in function stored in the _domain_tag_ file. The input and output of these functions is prescribed (see _domain_tag_ 
example documentation). The third output is reserved for new interesting links, that are automatically added to the URL addresses' 
queue of the _Scraper_ and will be scraped in the process. Two types of scraping can be executed:
  1. the input is a list of different URL addresses, which are scraped according to the same rules,
  2. the input is a list of values that are used to run a script on the **same** page; the results are then scraped.

The first type is the default behaviour, however running _start_ with the option `mp_func="follow_dests"` will execute the second type.

Initialization of the _Scraper_ object is done with the command:
```
Scraper(name, websites, num_of_threads=3, driver=None, to_save="", options=None, to_log="", restrictions=None, **kwargs)
```

## Parameters
The first two inputs are mandatory, others are optional with default values as stated above. Other values can be:
 * _name_: the name that will be used for logfiles, result files and in log messages.
 * _websites_: either a string with a URL address or a list of such strings. The first address will be used for restriction detection.
 * _num_of_threads_: specifies the number of concurrent threads to be used while scraping and consequently number od _Driver_ objects 
 to spawn.
 * driver: an existing _Driver_ object that will be used as a template for the _Scraper_ and its _Driver_ children. They inherit the 
 template driver's attributes and restrictions. The _options_, _restrictions_, and _kwargs_ parameters will be ignored even if 
 specified.
 * _to_save_: path to the map where a .csv file with results will be saved. If left empty, the process will not create a file. Given an
 already existing file will append additional information if the format is matching.
 * _options_: the default value initializes a headless (background) browser. A comprehensive list of other options can be found 
 [here](https://www.selenium.dev/selenium/docs/api/py/webdriver_firefox/selenium.webdriver.firefox.options.html); if we want a visible
 browser window, this can be set to an empty list `[]`. This parameter is ignored if _options_ are inherited from a _Driver_ object.
 * _to_log_: path to the logfile that will be filled with the _Driver_'s work progress.
 * _restrictions_: this parameter adds restriction pages that are not scraped. If left `None` the restrictions will be set by checking
 the domain's Robots.txt document. If the user does not want to check restrictions (__*not recommended*__), they can set this to empty
 list `[]`. This parameter is ignored if _restrictions_ are inherited from a _Driver_ object.
 * _kwargs_: additional keyword arguments that the _Driver_ objects will use to spawn. See the _Driver_ object documentation for more.
  These parameters are ignored if _kwargs_ are inherited from a _Driver_ object.

When a previously defined _Driver_ object is introduced into the _Scraper_ initialization, the initialization will skip the robots check
and just assume the restrictions (and restriction mode if it's `None`) from the original _Driver_ object. However, if _restrictions_ are
not `None`, the robots will still be checked at every domain change.

## Methods
Methods can be used with commands of shape `Scraper._method_`, where `_method_` is the desirable method. A _Scraper_ object has four 
methods:
 * `save_to_log(message, nblank=0, **kwargs)`: print a log record with _message_ to the monitor and to the logfile if the _Driver_ 
 parameter _to_log_ is specified. The logfile will automatically include a timestamp. The parameter _nblank_ adds leading newlines. 
 Additional keyword arguments (_kwargs_) can be specified. The method uses the same _kwargs_ as the base Python function _print_.
 * `start(func, links=None, sleeptime=3, tries=0, num_of_threads=None, mp_func="_follow_links", webdriver_log="", **kwargs)`: the initiator of scraping on each _Driver_ object according to instructions stored in a function _func_ in the _domain_tag_ 
 file. At the end the outputs of the _Driver_ objects are merged. If specified the logfile and end result file are also created. 
   * The _Scraper_ will connect each child _Driver_ to a page from the _links_ list and scrape it, automatically adding further found
   links (if _func_ is construced so) to the list. If left `None`then the original _Scraper_'s _websites_ parameter is used.
   * The _sleeptime_ parameter is the interval each child _Driver_ waits before connecting to the next item on the list of _links_.
   * The number of connection attempts is regulated by the parameter _tries_. Leaving it at 0 means that in type 1 scraping 15 attempts
   are allowed and in type 2 scraping 3 attempts are allowed.
   * If less pages than then the number of _Driver_ objects is needed to be scraped at the same time, the parameter _num_of_threads_ 
   can be used to limit the number of _Driver_ initializations. If the number is higher than the _Scraper.num_of_threads_ value, it's 
   ignored. The value `None` uses all _Drivers_ specified.
   * The parameter _mp_func_ defines which type of scraping will execute, the default executes type 1, while `"follow_dests"` executes 
   type 2.
   * The _webdriver_log_ and _kwargs_ parameters are _Driver_ parameters that are used by the children _Driver_ objects.\
    * **Note:** the _Driver_ children are always closed if scraping finished successfully. They can be reused again with the same 
    attributes and restrictions if a new _start_ method is called.
 * `_follow_links`: while technically a method, it should never be called by the user. This is the default programme that works in an 
 individual instance of a _Driver_ child to produce scraping of type 1. It's called (as a string) in the _Scraper.start_ method by the 
 parameter _mp_func_. It selects an unused URL address from the scraping list, feeds it to the _Driver_ and then executes the scraping 
 function (a _domain_tag_ function). Then the method collects the results of the scraping and adds them to the shared results 
 compilation. If a new relevant address is produced from scraping, then it's added to the list. This method keeps being called as long 
 as there are items in the list. After exhausting the list of items and if the _Driver_ child has been initialized by the _Scraper_ 
 object, this method automatically closes the _Driver.driver_ component. 
 * `follow_dests`: while technically a method, it should never be called explicitly by the user. This programme is used to execute 
 scraping of type 2. It's called (as a string) in the _Scraper.start_ method by the parameter _mp_func_. It starts a _Driver_ child 
 object, connects it to the first _Scraper.websites_ URL address and then selects an unused item from the scraping list and feeds it to 
 the _Driver_ according to the instructions in the scraping function (a _domain_tag_ function). Then the method collects the results of 
 the scraping and adds them to the shared results compilation. If a new relevant item is produced from scraping, then it's added to 
 the list. This method keeps being called as long as there are items in the list. After exhausting the list of items and if the
 _Driver_ child has been initialized by the _Scraper_ object, this method automatically closes the _Driver.driver_ component. 
