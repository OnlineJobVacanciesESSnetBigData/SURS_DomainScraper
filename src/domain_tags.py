"""
This is an example script that is used to create a scraping application with Scraper. It includes two example of
scraping functions with some possible mechanics showcased and an example of an auxiliary function. The scraping
functions have prescribed inputs and outputs.

It also includes the function main() and the __name__ == "__main__" code block, which is essential for the Scraper to
work correctly.
"""
# Some helpful imports:
from time import sleep  # Pause Python
from scraping_aux import send_buttons  # Pressing buttons on dynamic pages
# Useful exceptions and errors that might arise when working with a browser simulation
from selenium.common.exceptions import WebDriverException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait  # Explicit waits (wait until ... happens)
from selenium.webdriver.common.by import By  # Define WebElement by some characteristic
from selenium.webdriver.support import expected_conditions as ec  # Use expected WebElement actions on dynamic pages


def _auxiliary_func(*some_args, **other_kwargs):
    """
    This function is an auxiliary function for use in the main scraping functions. It is entirely up to the user what
    this function does and returns.

    :param some_args: user defined arguments for the auxiliary function
    :param other_kwargs: user defined keyword arguments for the auxiliary function
    :return: user defined output
    """
    ...
    return


def func_example(driver, **kwargs):
    """
    This is an example function of a crawler/scraper. Below you can find some useful instructions for tag handling and
    scraping on an internet page. While they are ordered according to usefulness, this order should not be followed
    when actually preparing a program. (Specifically, explicit waits should be set before running any driver methods).

    :param driver: the custom_driver.Driver object that is used to connect to the page
    :param kwargs: additional keyword arguments that can be used in the function; kwargs is a mandatory parameter, even
        when the user has no additional keyword arguments, it should be included.
    :return: three lists, first two are results that will be aggregated together across all drivers, the third is a list
        of items that will be added to the queue of items to be scraped in the current scraping process.
    """
    # The results should be defined as empty lists before start
    reslist1, reslist2, list_of_links_to_follow = [], [], []

    # Use an additional parameter from kwargs:
    parameter_value = kwargs.get("additional_par")

    # Finding tags on a static website
    reslist1.append([driver.soup.find("tags_example1", {"tag_atribute": "atr_value"}),  # find tag with attribute value
                     # find tag with characteristics given by additional parameter
                     driver.soup.find(parameter_value[0], {parameter_value[1]: parameter_value[2]})])
    reslist2.append(driver.soup.find_all("tags_example3"))  # find all tags of same name in the soup (list)

    list_of_links_to_follow.append(driver.soup.find_all("a").get("href"))  # extract all 'a' tags' 'href' values

    # Interacting with a dynamic website (clicking and inputing text)
    send_buttons(driver, "//xpath_to_event_tag[@attribute='value']")  # javascript click on tag with given xpath
    # input mimicking human behaviour (0.1 second delay between each character input)
    send_buttons(driver, "//xpath_to_event_tag[@input='value']", "text_to_input")
    send_buttons(driver, "//xpath_to_event_tag[@input='value']", pos=5)  # click on the 5th instance of the tag

    # Sometimes internet pages don't register JavaScript clicking. When this happens a secondary method might work.
    # This method is susceptible to overlaying elements on page!
    driver.driver.find_element_by_xpath("//xpath_to_unobscured_element").click()

    # Exlicitly waiting for scripts to execute
    WebDriverWait(driver.driver, 5).until(ec.element_to_be_selected((By.XPATH, "//waiting_el_xpath")))
    # wait at most 5 seconds or until the element with given xpath is selected
    WebDriverWait(driver.driver, 4).until(ec.visibility_of_element_located((By.ID, "id_value")))
    # wait at most 4 seconds or until the element with given id attribute is visible
    WebDriverWait(driver.driver, 10).until(ec.element_to_be_clickable((By.CLASS_NAME, "class_value")))
    # wait at most 10 seconds or until the element with given class attribute is clickable

    # If the WebDriverWait does not find the element for some, it raises an exception:
    try:
        WebDriverWait(driver.driver, 10).until(ec.element_to_be_clickable((By.CLASS_NAME, "class_value")))
    except (TimeoutException, ElementClickInterceptedException, WebDriverException, Exception):
        '''code to execute if element not clickable'''
        ...
    # Most common exceptions are
        #     - TimeoutException: loading of page/element has not concluded in allowed time
        #     - ElementClickInterceptedException: another element is obscuring the chosen one
        #     - WebDriverException: general error; the webdriver could not connect to address due to an unknown reason

    # Implicitly wait:
        # Everytime you call a method on Driver.driver it will wait 10 seconds before
        # returning an error. This setting is set for life or until changed.
    driver.driver.implicitly_wait(10)

    #  Absolute wait:
    sleep(0.5)  # sleep for 0.5 seconds

    # It is recommended that you resoup your Driver object before you continue working with tags:
    driver.resoup()

    # Other instructions
    ...
    return reslist1, reslist2, list_of_links_to_follow if list_of_links_to_follow else []


def second_func(driver, **kwargs):
    """
    A second example function to scrape different characteristics than the func_example(). This function is used to
    dynamically interact with the driver and input some item on the last page used on the Scraper
    (the Scraper.current_page parameter). To correctly use this function, the user should specify "follow_dests" in the
    "mp_func" parameter of the Scraper.start method (otherwise the Scraper will attempt to use the item as the URL
    address).

    The input MUST include a kwargs parameter with the keyword 'input_duo' which includes the item, that is used in the
    interaction, and an integer, which represents number of unsuccessfully attempted uses of item on the page.
    :param driver:
    :param kwargs:
    :return:
    """
    # Like before the results should be defined as empty lists before start
    reslist1, reslist2, list_of_items_to_follow = [], [], []
    # The obligatory kwargs element 'input_duo'
    item, retry_on_item = kwargs.get("input_duo")

    # Some auxiliary function can be used for better control
    _auxiliary_func(*{"some", "args", ...}, **{"keyword1": "some", "keyword2": "kwargs", ...: ...})

    # Example of an unsuccessful interaction should the user wish to retry. The output should be of shape
    # [...], [...], [(item, retry_on_item + 1)] and the third list will be added to the scraping list in the current
    # scraping
    if ...:
        return [...], [...], [(item, retry_on_item + 1)]

    # Other instructions
    ...
    return reslist1, reslist2, list_of_items_to_follow if list_of_items_to_follow else []


def main():
    """
    This file can be used as a script in terminal ba calling it with -m flag. It is executed with the below
    characteristics.

    :return: three lists with results defined in the func_example definition; it also creates a file with
    some basic statistics
    """
    from custom_scraper import Scraper  # Import the Scraper object
    from scraping_aux import numbers_report  # Some auxiliary functionalities

    # Initial parameters for the Scraper
    shop_name = "shop_name"  # The Scraper name
    save_dir = "path/to/save/dir"  # The path to the save folder
    log_dir = "path/to/log/dir"  # The path for the logfile
    pages_to_scrape = ["A", "page", "or", "list", "of", "pages", "to", "scrape"]  # A list of interesting URL addresses
    items_to_scrape = ["Item1", "Item2", "Item3"]  # A list of interesting items used on the Scraper page dynamically

    # Scraper initialization. Since the "to_save" parameter is not used, the results WILL NOT be saved.
    shop_scraper = Scraper(shop_name, pages_to_scrape, to_log=log_dir)

    # Scraping a list of URL addresses.
    return1, return2, return3 = shop_scraper.start(func_example)

    # We can change Scraper behaviour by attributes manipulation. In the below example, the Scraper WILL save the
    # results from now on.
    shop_scraper.to_save = save_dir

    # Scraping the result of dynamic use of items on the current page of the Scraper
    return_items1, return_items2, return_items3 = shop_scraper.start(second_func,
                                                                     [(item, 0) for item in items_to_scrape],
                                                                     mp_func="follow_dests")

    # Example of use of the numbers report, reporting on the results in the save directory.
    numbers_report(return_items1, save_dir)

    # The return statement is not mandatory. It's a typical Python function conclusion and has no special mechanics in
    # the scope of scraping.
    return return_items1, return_items2, return_items3


"""
The __name__ == "__main__" code block is essential when working with the multiprocessing module. Without it, the chance
of crashes and unsuccessful attempts at multi-threading increases dramatically. In python language this code block 
represents instructions that are executed as a script.
 
This means, this can be used to create real applications in python without use of running an interpreter first and then 
submitting code to it. By running a cmd (Windows) or terminal (Linux) command 'python -m domain_tag' from the 
relevant folder, every action in the function main() will be executed.

Using this script properly is therefore essential. It should include at least 2 functions:
 - a set of instructions for the Scraper object that is executed in the Driver object to execute the scraping process,
 - the main() function that contains definitions and initializations of the Driver/Scraper processes and operations on
   their results.
   
If multiple different scraping processes are supposed to be executed on the same domain, just write multiple scraping
functions and call them in the Scraper.start method in the main() function like in the second_func example above. 
"""
if __name__ == "__main__":
    main()
