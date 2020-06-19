# Technical documentation for Slovenian scraping robot - a _domain_tag_ file example
This document describes the module _domain_tag_, the idea behind its functionality, and includes a few examples of scraping functions. 
It is advised that a simultaneous read of the _domain_tag.py_ file is done while reading this document.

The module runs in Python version 3.5 or higher. The functions are entirely user defined except for the inputs and outputs. Therefore 
module requirements are dependent on the user. A few most used in our examples are used below:
 * sleep (from module time)
 * send_buttons (from custom module scraping_aux)
 * WebDriverException, TimeoutException, ElementClickInterceptedException (from module selenium.common.exceptions)
 * WebDriverWait (from module selenium.webdriver.support.ui import WebDriverWait)
 * By (from module selenium.webdriver.common.by)
 * expected_conditions (from module selenium.webdriver.support)

The _domain_tag_ script is an example of the script used to create a scraping application with Scraper. It includes two example of
scraping functions with some possible mechanics showcased and an example of an auxiliary function. The scraping functions have 
prescribed inputs and outputs.

It also includes the function _main_ and the `__name__ == "__main__"` code block, which is essential for the _Scraper_ to work 
correctly.

## Scraping function's type
_Scraper_ has two types of scraping (for more details, see documentation on _Scraper_), which differ in the input to the scraping 
function. Both types are used  for scraping by including them into the _Scraper.start_ method as the parameter _func_. By default the 
type used for scraping is of type 1, type 2 must be specified by also setting the parameter "mp_func" to the value `"follow_dests"`.

### Type 1
The default type is scraping of a list of URL addresses and the input to the scraping function are obligatory a _Driver_ object and 
keyword elements that may include any custom-made arguments shared between each _Driver_ process. If a URL address fails to connect, it 
can be added to the scraping list by returning it as an element in the third output of the scraping function. However, this may lead to 
an infinite loop when the URL page non-existent or unresponsive.

### Type 2
The other type is scraping of one page with a dynamic input, which is represented by a list of all items to be inputted as the second 
parameter in the call to the _Scraper.start_ method. However, the shape of the list is in effect of shape `[(item1, #1), (item2, #2), 
...]` where the `#` represent the integer value of attempts to use the respective item. This is done, because each item is an external 
parameter, and the _Scraper_ alone does not know how many times it has been tried before. But in a situation, when an item does not 
produce correct results at all and the output is just another addition to the scraping list, there is risk of an infinite loop.

Therefore the output of a an unsuccessful use of the item should result in the addition of a pari `(item, # + 1)` to the scraping list.
By default the numbers of attempts for each item is three, but this can be changed generally by the _Scraper_ parameter _tries_ and
individually by lowering the input `#` value.

The scraping list itself is coded as a keyword argument with key `"input_duo"` in code of the scraping_function.

## Scraping function - type 1
The type 1 scraping function is coded in the file with:
```
def scraping_func1(driver, **kwargs):
    
    output1, output2, links_to_scrape = [], [], []
   
    ...
   
    return output1, output2, [] if not links_to_scrape else links_to_scrape
```
where `...` denotes custom-made code. \
If new/unconnected links are to be added (again) to the scraping list, they must be put into the third output list (`links_to_scrape`).

The functionis called by the _Scraper.start_ method as the first parameter. 
```
Scraper.start(scraping_func1, ...)  # "..." denotes optional parameters
```
Each _Scraper_ process automatically passes its _Driver_ object as the _driver_ parameter. As is better explained in the _Scraper_ 
documentation, a second __unnamed__ argument that must be a list can also be passed to the _start_ method. The list should contain links
for the _Scraper_ to load and scrape. Any additional _kwargs_ arguments given to the _start_ method are then passed directly to the 
_scraping_func_ function as a dictionary called _kwargs_.

Technically speaking, a standalone scraping process can be also run with this function on a _Driver_ object. Of course this process only
scraped the currently loaded page. The standalone process is started by calling:
```
driver = Driver()
driver.get("a page you want to scrape")
outputs = scraping_func(driver, ...)  # "..." denotes optional parameters
driver.driver.quit()  # You should always close a driver after use
```

## Scraping function - type 2
The type 2 scraping function is coded in the file with:
```
def scraping_func2(driver, **kwargs):
    
    if kwargs.get("input_duo") is None:
        raise KeyError("Parameter 'input_duo' is missing!")
    item, nitem = kwargs.get("input_duo")

    output1, output2, items_to_scrape = [], [], []
   
    ...
   
    return output1, output2, [] if not items_to_scrape else items_to_scrape
```
where `...` denotes custom-made code. \
If new/unconnected links are to be added (again) to the scraping list, they must be put into the third output list (`links_to_scrape`).
While raising the error is not absolutely essential when `input_duo` is missing in the input, we recommend that is left in the code to 
remind users of the special format for the list of items.

The function is called by the _Scraper.start_ method as the first parameter, a list of items for dynamic interaction, and specification
of the keyword argument `mp_func="follow_dests"`.
```
# "..." denotes optional parameters
Scraper.start(scraping_func2, [(item1, 0), (item2, 0), ], mp_func="follow_dests", ...)
```
Each _Scraper_ process automatically passes its _Driver_ object as the _driver_ parameter. It should be connected to the correct 
interactive address. A second __unnamed__ argument *must* be a list is also passed and each process takes one element at a time. Lastly,
the parameter _mp_func_ must be present to signal to the _start_ method, that we wish to input items dynamically. Any additional 
_kwargs_ arguments given to the _start_ method are then passed directly to the _scraping_func_ function as a dictionary called _kwargs_.

Technically speaking, a standalone scraping process can be also run with this function on a _Driver_ object. Of course this process only
inputs one item. The item **must** be denoted by the keyword argument _input_duo_. The standalone process is started by calling: 
```
driver = Driver()
driver.get("a page you want to interact with")
outputs = scraping_func(driver, input_duo=(item, #), ...)  # "..." denotes optional parameters
driver.driver.quit()  # You should always close a driver after use
```
## The `__name__ == "__main__"` code block and the _main_ function
The _Scraper_ object's main advantage is a concurrent scraping with possibility of running browser scripts. The multiprocessing module 
is used for running multiple processes of scraping at once. However for the process to work correctly, a special feature must be present
in the code.

This is the `__name__ == "__main__"` code block. To read, why this is an essential part of the code (especially in Windows), see this
[link](https://docs.python.org/2/library/multiprocessing.html#windows). The code block is needed to protect the "entry point" of the 
programme, which in this case is the _scraping_fun_, therefore the block is put at the end of the _domain_tag_ file. The full 
functionality of the code block is achieved when the split into multiple processes is applied as a Python script and not as a function. 

We also explot this fact to transform the _domain_tag_ file into a fully working script. To simplify the code for the user, we define 
a _main_ function without any paramters where a _Scraper_ method is initialized and executed. The function is then the only thing 
called in the code block. Conversely, we could just put everything from the _main_ function into the code block, but this would require
a lot of copy-pasting if the user wanted to run the scraping in a Python console. This way only one command needs to be run.

## Auxiliary functions
For more complex scrapings some auxiliary functions will be required that are used in the scraping function. The user can and is
encouraged to write their own auxiliary functions in this file. The auxiliary functions don't have any prescribed shape and it's 
entirely up to the user what and how they work.

As an example, we mostly use auxiliary functions to search for the "next page" in the HTML of the current page (static page), or input
the desired date into a calendar to run a date-dependent script (dynamic page).
