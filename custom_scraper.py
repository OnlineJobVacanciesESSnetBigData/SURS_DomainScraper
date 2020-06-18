from custom_driver import Driver  # Custom object that creates a storage holder for connections and info to domains
import traceback  # Working with error tracebacks
import csv  # Module to work .csv files
import time  # Module to work with time objects
from datetime import datetime  # Module to work with datetime objects; including mathematical operations
import os  # Module with tools for working with files and folders
import sys  # Module with additional system tools
from multiprocessing import Queue, Process, Manager  # Module for multi-thread work
from multiprocessing.queues import Empty  # Multi-thread queue functionality
from selenium.common.exceptions import WebDriverException  # Module with WebDriver exception rules

# Win10 fix for printing into a custom stdout (e.g. logfile)
import win_unicode_console
win_unicode_console.enable()


class Scraper(object):
    """
    An object which defines the options for scraping: name of scraper, website(s) to scrape, number of concurrent
            threads, paths to save files and logs, Driver object options, etc.
    It has the following methods:
    __init__: definition of object.
    save_to_log: prints to display and saves a message if the logpath is given.
    start: starts the crawling-scraping process given the function of scraping 'func'. Returns 3 lists: a list of lists
        of characteristics of the items, a list of possible links to follow, and a list of unsuccessfull connection
        addresses.
    """

    def __init__(self, name, websites, num_of_threads=3, driver=None, to_save="",
                 options=None, to_log="", restrictions=None, **kwargs):
        """
        The __init__ file for a Scraper object. In the process of initialization it populates the restrictions list if
        so set.
        :param name:  the name of the object.
        :param websites: list of meaningful websites of this object. Careful: the object will automatically assume
        restrictions from the first website in the list, if restrictions are enabled.
        :param num_of_threads: the number of threads to be used for scraping of website(s). Also the number of Driver
        object clones that the Scraper will spawn to connect to the websites.
        :param driver: link an existing driver. If not, a new Driver object will be created.
        :param to_save: path to the savefile.
        :param options: a list with options for the Driver object
        :param to_log: path to the logfile.
        :param restrictions: a list of restrictions for the webdrivers. If set to empty list, the restrictions will be
        ignored.
        :param kwargs: additional key-word arguments
        """
        self.name = name
        cl_driver = True
        if num_of_threads < 1:
            raise ValueError("Number of threads must be positive!")
        self.num_of_threads = num_of_threads
        self.to_save = to_save
        self.to_log = to_log if driver is None or not driver.to_log else driver.to_log
        self.websites = [websites] if isinstance(websites, str) else (websites if isinstance(websites, list) else [])
        if not self.websites or not all([isinstance(page, str)for page in self.websites]):
            raise TypeError("Parameter \'websites\' is must be a list of strings")
        if driver is None:
            driver = Driver(name=self.name, options=options, restrictions=restrictions,
                            to_log=to_log, proxy_port=kwargs.get("proxy_port"), profile=kwargs.get("profile"),
                            executable_path=kwargs.get("executable_path"), bins_path=kwargs.get("bins_path"))
        else:
            cl_driver = False
        if not isinstance(driver, Driver):
            raise TypeError("Scraping driver must be object of type custom_driver.Driver")
        if self.websites and restrictions is None:
            self.save_to_log("\tInitializing scraper with restrictions for robots")
        driver.get(self.websites[0])
        self.save_to_log("Creating driver clones. Number of clones: %d" % self.num_of_threads, 1)
        self.drivers = [driver.export_Driver() for _ in range(self.num_of_threads)]
        for n, dr in enumerate(self.drivers):
            dr.name = self.name + "_cln%s" % n
            if dr.to_log:
                dr.to_log += "%s" % n
        if cl_driver:
            driver.driver.quit()
            del driver

    def save_to_log(self, message, n=0, **kwargs):
        """
        Displays a message and saves it to the logfile if a logpath was given.
        :param message: the message to be displayed.
        :param n: number of strating blank rows (for better readability in the logfile)
        :param kwargs: additional key-word arguments.
        :return: a displayed message which might be stored in given logfile.
        """
        print(u"%s%s" % ("\n"*n, message))
        if self.to_log:
            with open(self.to_log, "a", encoding="utf8") as logfile:
                sys.stdout = logfile
                print("%s%s:\t%s" % ("\n"*n, datetime.now().strftime("%d.%m.%Y %H:%M:%S"), message), **kwargs)
                sys.stdout = sys.__stdout__

    def start(self, func, links=None, sleeptime=3, tries=0, num_of_threads=None, mp_func="_follow_links",
              webdriver_log="", **kwargs):
        """
        Starts the process of crawling-scraping with given function 'func'. If not specified by the 'links' parameter
        the Scraper.websites list is scraped.
        :param func: the function with instructions for scraping.
        :param links: links to be scraped. If left None, the list Scraper.websites will be scraped.
        :param sleeptime: the time interval between each connection on a Driver object.
        :param tries: number of tries if reached a timeout.
        :param num_of_threads: number of threads to be used for this work, cannot be higher than the Scraper number of
        threads
        :param mp_func: selection of the multiprocessing function. Defaults to _follow_links
        :param webdriver_log: where should the webdriver's log be saved to a file. Defaults to the src/logs dir. If None
        the log is not saved to a file but printed into the console.
        :param kwargs: additional key-word arguments.
        :return: 3 lists: a list of lists of characteristics of the items, a list of possible links to follow, and a
        list of unsuccessfull connection addresses.
        """
        tries = tries if tries else (15 if mp_func == "_follow_links" else 3)
        kwargs.update({"webdriver_log": webdriver_log})
        mp_func = getattr(Scraper, mp_func)
        links = self.websites if links is None else links
        links = [links] if isinstance(links, (str, tuple)) else links
        self.save_to_log("Number of pages to scrape: %d" % len(links))
        if num_of_threads is None:
            num_of_threads = self.num_of_threads
        if num_of_threads > self.num_of_threads:
            self.save_to_log("Number of specified threads is higher than the thread allotment of the Scraper.\n"
                             "Number of threads used now equals the allotment number: %s" % self.num_of_threads)
            num_of_threads = self.num_of_threads
        if num_of_threads < 1:
            raise ValueError("Number of threads must be positive!")
        self.save_to_log("Starting crawling/scraping process with number of webdrivers: %d%s"
                         % (num_of_threads, "\n\n"), 1)
        q = Queue()
        with Manager() as manager:
            wait_proc = manager.dict(zip([dr.name for dr in self.drivers][:num_of_threads],
                                         [False for _ in range(num_of_threads)]))
            characteristics = manager.list()
            following_links = manager.list()
            scrape_list = manager.list(links)
            unsuccess = manager.list()
            while scrape_list:
                q.put(scrape_list.pop(0))
            proc_list = []
            for th in range(num_of_threads):
                proc_list.append(Process(target=mp_func,
                                         args=(func, q, characteristics, following_links, unsuccess,
                                               self.drivers[th], sleeptime, tries, wait_proc),
                                         kwargs=kwargs))
            for p in proc_list:
                p.start()
                time.sleep(sleeptime)
            for p in proc_list:
                p.join()
                time.sleep(sleeptime)
            self.save_to_log("\tTransforming threaded results into list data, this might take some time...")
            characteristics, following_links, unsuccess = characteristics[:], following_links[:], unsuccess[:]
        if self.to_log:
            ordered_logs = []
            for th in range(num_of_threads):
                with open(self.drivers[th].to_log, "r", encoding="utf8") as logfile_tmp:
                    log = logfile_tmp.readlines()
                    ordered_logs.extend(log)
                os.remove(self.drivers[th].to_log)
            with open(self.to_log, "a", encoding="utf8") as logfile:
                logfile.writelines(sorted(ordered_logs))
        if self.to_save:
            with open(self.to_save, "a+", encoding="utf8", newline="") as cs:
                writer = csv.writer(cs, delimiter=";", quotechar="\"")
                writer.writerows(characteristics)
        return characteristics, following_links, unsuccess

    @staticmethod
    def _follow_links(func, queue, shared_list, shared_following, failed,
                      driver, sleeptime, tries, wait_dict, **kwargs):
        """
        An auxiliary function for multithreading. Manages data exchange between threads and queue of addresses to
        connect to. After the queue is exhausted closes all webdrivers.
        :param func: the function with instructions for scraping.
        :param queue: the queue with addresses to connect to.
        :param shared_list: a list of results (first list) from the function. Shared between all threads.
        :param shared_following: a list of results (second list) from the function. Shared between all threads.
        :param failed: a list of URL addresses that were unsuccessfully connected to during the run.
        :param driver: the Driver object clone that connects to websites.
        :param sleeptime: the time interval between each connection on a Driver object.
        :param tries: number of tries if reached a timeout.
        :param wait_dict: a dictionary, shared between all threads, where the status of each thread is shown. Used for
        webdriver closing synchronization.
        :param kwargs: additional key-word arguments.
        :return: 3 lists: a list of lists of characteristics of the items, a list of possible links to follow, and a
        list of unsuccessfull connection addresses.
        """
        fresh = driver.__fresh__
        qto = kwargs.get("queue_timeout") if kwargs.get("queue_timeout") else 5
        kwargs.update({"n": 0, "page_queue": queue})
        while not all(wait_dict.values()):
            time.sleep(sleeptime)
            try:
                link = queue.get(True, qto)
            except Empty:
                wait_dict.update({driver.name: True})
                continue
            else:
                wait_dict.update({driver.name: False})
            counter = 0
            break_ = True
            while break_ and counter < tries:
                try:
                    if not driver.get(link, n=tries-counter, webdriver_log=kwargs.get("webdriver_log"),
                                      timeout=kwargs.get("timeout"), th=driver.name):
                        driver.save_to_log("\tDriver %s: COULD NOT CONNECT TO ADDRESS %s\n\tSkipping crawling..."
                                           % (driver.name, link))
                        failed.append(link)
                        break_ = False
                    else:
                        counter = tries
                except WebDriverException:
                    driver.save_to_log("Driver %s: Error while connecting to address %s, retrying..."
                                       % (driver.name, link))
                    counter += 1
                    continue
            if not break_:
                continue
            try:
                reslist, resfollowing, next_page = func(driver, **kwargs)
            except Exception as e:
                driver.save_to_log("\tCLOSING DRIVER %s DUE TO ERROR: " % driver.name +
                                   type(e).__name__ + ("\n\t" + str(e) if str(e) else "") + traceback.format_exc())
                if kwargs.get("__debugmode__") is None or not kwargs.get("__debugmode__"):
                    driver.driver.quit()
                raise e
            for new_link in next_page:
                queue.put(new_link)
            shared_list.extend(reslist)
            shared_following.extend(resfollowing)
            kwargs.update({"n": kwargs.get("n") + 1})
        driver.save_to_log("\t\t\tCLOSING Driver %s, this might take some time..." % driver.name)
        if all((driver.is_alive(), not driver.__fresh__, fresh)):
            driver.driver.quit()
            del driver.driver
        return

    @staticmethod
    def follow_dests(func, queue, shared_list, shared_following, failed,
                     driver, sleeptime, tries, wait_dict, **kwargs):
        """
        An auxiliary function for multithreading. Manages data exchange between threads and queue of addresses to
        connect to. After the queue is exhausted closes all webdrivers.
        :param func: the function with instructions for scraping.
        :param queue: the queue with addresses to connect to.
        :param shared_list: a list of results (first list) from the function. Shared between all threads.
        :param shared_following: a list of results (second list) from the function. Shared between all threads.
        :param failed: a list of URL addresses that were unsuccessfully connected to during the run.
        :param driver: the Driver object clone that connects to websites.
        :param sleeptime: the time interval between each connection on a Driver object.
        :param tries: number of tries if reached a timeout.
        :param wait_dict: a dictionary, shared between all threads, where the status of each thread is shown. Used for
        webdriver closing synchronization.
        :param kwargs: additional key-word arguments. MUST INCLUDE THE ARGUMENT 'input_duo': a tuple of parameter to
        input on site and number of executed tries.
        :return: 3 lists: a list of lists of characteristics of the items, a list of possible links to follow, and a
        list of unsuccessfull connection addresses.
        """
        fresh = driver.__fresh__
        qto = kwargs.get("queue_timeout") if kwargs.get("queue_timeout") else 5
        kwargs.update({"n": 0, "page_queue": queue})
        while not all(wait_dict.values()):
            time.sleep(sleeptime)
            try:
                kwargs.update({"input_duo": queue.get(True, qto)})
            except Empty:
                wait_dict.update({driver.name: True})
                continue
            else:
                wait_dict.update({driver.name: False})
            counter = 0
            break_ = True
            # In the case of a number of tries over limit, the program stops trying to connect
            if kwargs.get("input_duo")[1] >= tries:
                break_ = False
                driver.save_to_log("\tReached maximum number of allowed tries on %s" % driver.name)
            # Reconnect to the original link only in the case when the link isn't the same (w/ or w/o trailing '/')
            while break_ and (counter + kwargs.get("input_duo")[1]) < tries and \
                (True if driver.driver is None else (driver.current_url != driver.driver.current_url and
                                                     driver.current_url + "/" != driver.driver.current_url)):
                try:
                    if not driver.get(driver.current_url, n=tries-counter,
                                      webdriver_log=kwargs.get("webdriver_log"),
                                      timeout=kwargs.get("timeout"), th=driver.name):
                        driver.save_to_log("\tDriver %s, destination duo %s: COULD NOT CONNECT TO ADDRESS %s"
                                           % (driver.name, str(kwargs.get("input_duo")[0]), driver.current_url))
                        failed.append(kwargs.get("input_duo"))
                        break_ = False
                    else:
                        counter = tries
                except WebDriverException:
                    driver.save_to_log("Driver %s: Error while connecting to address %s, retrying..."
                                       % (driver.name, driver.current_url))
                    counter += 1
                    continue
            if not break_:
                continue
            try:
                reslist, resfollowing, next_page = func(driver, **kwargs)
            except Exception as e:
                driver.save_to_log("\tCLOSING DRIVER %s DUE TO ERROR: " % driver.name
                                   + type(e).__name__ + ("\n\t" + str(e) if str(e) else "") + traceback.format_exc())
                if kwargs.get("__debugmode__") is None or not kwargs.get("__debugmode__"):
                    driver.driver.quit()
                raise e
            for new_link in next_page:
                queue.put(new_link)
            shared_list.extend(reslist)
            shared_following.extend(resfollowing)
            kwargs.update({"n": kwargs.get("n") + 1})
        driver.save_to_log("\t\t\tCLOSING Driver %s, this might take some time..." % driver.name)
        if all((driver.is_alive(), not driver.__fresh__, fresh)):
            driver.driver.quit()
            del driver.driver
        return
