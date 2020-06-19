# Technical documentation for Slovenian scraping robot - the _Driver_ object
This document describes the module _custom_driver_, its main object _Driver_ and their mechanics in detail. The module runs in Python 
version 3.5 or higher. The object and methods require the following modules and methods to work:
 * BeautifulSoup (from module bs4) and HTML parser _lxml_,
 * webdriver (from module selenium),
 * Options (from module selenium.webdriver.firefox.options),
 * FirefoxBinary (from module selenium.webdriver.firefox.firefox_binary),
 * TimeoutException (from module selenium.common.exceptions),
 * WebDriverException (from module selenium.common.exceptions),
 * datetime (from module datetime),
 * urlparse (from module urllib.parse),
 * warn (from module warnings),
 * module re,
 * module http.client,
 * module socket,
 * Command (from module selenium.webdriver.remote.command),
 * module win_unicode_console.

## Initialization
While the object _Driver_ is used for a simulation of a browser, the browser window itself is an attribute of the object. The window 
only opens with the first use of the method _get_ (below) after the _Driver_ initialization. The object _Driver_ can be initialized 
with parameters:
```
Driver(executable_path, bins_path, options=None, restrictions=None, to_log="", proxy_port=None, profile=None,
       name="cstmdr", n=15, user_agent_string=None)
```
## Parameters
All of the inputs but the two executables are optional and the default values can be seen above. Other values can be:
 * _executable_path_: the path of the mandatory geckodriver executable
 * _bins_path_: the path of the mandatory Firefox executable
 * _options_: the default value initializes a headless (background) browser. A comprehensive list of other options can be found 
 [here](https://www.selenium.dev/selenium/docs/api/py/webdriver_firefox/selenium.webdriver.firefox.options.html); if we want a visible
 browser window, this can be set to an empty list `[]`.
 * _restrictions_: this parameter adds restriction pages that are not scraped. If left `None` the restrictions will be set by checking
 the domain's Robots.txt document. If the user does not want to check restrictions (__*not recommended*__), they can set this to empty
 list `[]`.
 * _to_log_: path to the logfile that will be filled with the _Driver_'s work progress.
 * _proxy_port_: a list of five (key, value) couples, where keys are proxy port addresses and values are addresses' ports. If left 
 `None` a set of five `("", 0)` couples is used. The couples are used in order for the protocols:
   * http,
   * https, 
   * ssl, 
   * ftp and 
   * socks.
 * _profile_: a Firefox profile object, if `None` then a _carte_ _blanche_ profile is created and used.
 * _name_: name of the driver to be used in logs.
 * _user_agent_string_: the name of the user agent used in scraping 

## Attributes
Additionally, some automatically set attributes are also available after initialization of the object by calling `Driver._attr_` where
`_attr_` is the chosen attribute:
 * _driver_: a Selenium Webdriver object that is running the browser.
 * _current_url_: the currently inputted URL, `None` if no connection was attempted yet. If a redirect happened, this remains the
 original URL. For the actual current URL use the Driver.driver.current_url command.
 * soup: the initial HTML code (also called soup) on the current page. _Warning:_ on dynamic pages, this _does not_ change automatically. 
 To update the soup use the _Driver_ method _resoup_ (below).
 * _http_, _domain_, _path_, _params_, _query_, _fragment_: the URL address parts as outputted by the _urllib.parse.urlparse_ method.
 * _n_: number of allowed retries on unsucessful connects.
 * _meta_: a Python dictionary with additional keyword arguments for optional use. Empty on default.

## Methods
Methods can be used with commands of shape `Driver._method_`, where `_method_` is the desirable method. A _Driver_ object has nine 
methods:
 * `save_to_log(message, nblank=0, kwargs)`: print a log record with _message_ to the monitor and to the logfile if the _Driver_ 
 parameter _to_log_ is specified. The logfile will automatically include a timestamp. The parameter _nblank_ adds leading newlines. 
 Additional keyword arguments (_kwargs_) can be specified. The method uses the same _kwargs_ as the base Python function _print_.
 * `get(link=None, n=None, webdriver_log="", timeout=None, th="")`: connect to the address _link_ with the _Driver_
 object. At first use the preferences for user agent string, proxy ports, Firefox profile and Firefox options are set, including the
 timeout interval with parameter _timeout_. This method updates most of the _Driver_ object's attributes with every use. If the 
 _Driver_'s _restrictions_ are `None` or non-empty, and the _domain_ attribute is different then the previous value, then a robots check
 is also excuted. In case of unsucessful connections, _n_ retries are attempted if _n_ is given, otherwise the _Driver_'s value is used.
   The _webdriver_log_ parameter is a special log for ultra-detailed notes of the Selenium API. These are mostly not useful to the 
 normal user and can therefore be set to empty. However, if the user wishes to read these logs, a path can be selected where they will be
 saved.  
 __*VERY IMPORTANT*: it is recommended that every _driver_ instance is closed after use with the command `driver.driver.quit()` where
`driver` is the name of the _Driver_ object.__
 * `resoup()`: updates the _Driver_'s _soup_ attribute.
 * `complete_link(link="")`: either returns the _current_link_ completed to full URL shape or, given the _link_ parameter, completes 
 the given string to the full URL shape. The full shape is _http(s)://ww<span>w.<span>domain/link_path_and_params_.
 * `is_alive()`: check if the _Driver_ object is functional.
 * `check_robots(agent="*", **kwargs)`: checks if the Robots.txt (or robots.txt) document restrict access to any pages on the domain 
 to our agent __and__ any other agent specified in the _agent_ parameter. Additional keyword arguments can be specified: 
   * _n_ (with default value 2) limits the number of allowed connections to the document and
   * _th_ argument sets the name of the _Driver_ for the log in the robot checking process.
 * `robots_deny(link=None)`: return restrictions relevant for the _Driver_' current page, otherwise returns `False`. If _link_ then
 its address is used for relevance.
 * `export_Driver()`: creates a copy of the _Driver_ object with the same attributes and a non-active _driver_.
 * `add_to_meta(values, keywords=None)`: adds items to the _meta_ dictionary. If only _values_ is defined and it's a dictionary or 
 couple, then the first value is used as keyword and the second as the value to be changed/added to the _meta_. If it's a list, then 
 default keywords `item#` where the `#` represents the number of items are used to update/expand the dictionary.
 
If the page is static, then all the information needed is stored in the _Driver_'s _soup_ attribute. To understand how to use soup 
extraction check [here](https://www.crummy.com/software/BeautifulSoup/bs4/doc/). On dynamic pages most of the work is done using its
_driver_ attribute. It can be used to click buttons, find webelements, wait for DOM changes much more. For more information on these 
mechanics read [Python Selenium guides](https://selenium-python.readthedocs.io/).

__*ONCE AGAIN*: it is recommended that every _Driver.driver_ instance is closed after use with the command `driver.driver.quit()` where
`driver` is the name of the _Driver_ object.__
