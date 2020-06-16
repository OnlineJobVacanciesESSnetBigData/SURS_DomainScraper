# Some helpful imports:

from time import sleep
from scraping_aux import send_buttons, numbers_report
from selenium.common.exceptions import WebDriverException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec


def func_example(driver, **kwargs):
    """
    This is an example function of a crawler/scraper. Below you can find some useful instructions for tag handling and
    scraping on an internet page. While they are ordered according to usefulness, this order should not be followed
    when actually preparing a program. (Specifically, explicit waits should be set before running any driver methods).

    :param driver: the custom_driver.Driver object that is used to connect to the page
    :param kwargs: additional keyword arguments that can be used in the function
    :return: three lists, first two are results that will be aggregated together across all drivers, the third is a list
        of links that will be added to the queue of links.
    """
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
        pass
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

    return reslist1, reslist2, list_of_links_to_follow if list_of_links_to_follow else []


def main():
    """
    This file can be used as a script in terminal ba calling it with -m flag. It is executed with the below
    characteristics.

    :return: three lists with results defined in the func_example definition; it also creates a file with 
    some basic statistics
    """
    from custom_scraper import Scraper
    shop_name = "shop_name"
    save_dir = "path/to/save/dir"
    log_dir = "path/to/log/dir"

    pages_to_scrape = ["A", "page", "or", "list", "of", "pages", "to", "scrape"]
    shop_scraper = Scraper(shop_name, pages_to_scrape, to_log=log_dir,  to_save=save_dir)
    return1, return2, return3 = shop_scraper.start(func_example)
    number_reports(return1, save_dir) 
    return return1, return2, return3


if __name__ == "__main__":
    main()
