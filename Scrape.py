#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=UTF-8

# This library holds definitions for crawling and scraping of job portals. Each job portal has unique tags and therefore
# the number of such libraries is the same as the number of different job portals.

from bs4 import BeautifulSoup  # HTML parsing
from selenium import webdriver  # simulation of a browser of person-like begaviour on webpages
from selenium.webdriver.firefox.options import Options  # options to the simulation browser
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary  # binaries to the simulation browser
from selenium.common.exceptions import TimeoutException  # errors due to timeouts on connections
import urllib.request as url  # connections to an internet page
import time  # timing and calculating with time
from datetime import datetime  # formatting dates
import csv  # reading and writing csv files
import sys  # system-specific parameters and functions
import os  # miscellaneous operating system interfaces
import re  # regular expressions
from multiprocessing import Process, Queue  # parallel processing and shared queueing
import signal  # set handlers for asynchronous events


def _find_next_page(soup):
    '''
    Finds the current pages' tags that correspond to the 'next page' tag. Returns a string that is either the link to
    the next page or the tag that the should be clicked in the selenium webdriver to be accessed. The last page
    with no next page returns an empty string.

    The following is an example and has to be adequately adjusted to individual pages.

    :param soup: a BeautifulSoup object from current page's HMTL
    :return: a string with the link or tag attribute value to the next page
    '''
    next_page = 0
    # A straight-forward example
    if soup.find("a", title="next page"):
        next_page = soup.find("a", title="next page").get("href")
    # An example where the proper link is general and hidden behind a different tag
    elif soup.find("li", {"class": "PagedList-Next"}):
        next_page = soup.find("li", {"class": "PagedList-Next"}).find("a").get("href")
    # An example where the proper link is general and the next page has to be found relative to the current one
    elif soup.find("ul", {"class": "pagination"}).find("li", {"class": "selected"}):
        soup_selected = soup.find("ul", {"class": "pagination"}).find("li", {"class": "selected"})
        number_of_next = int(soup_selected.get_text()) + 1
        if str(number_of_next) in soup.find("ul", {"class": "pagination"}).get_text():
            next_page = soup_selected.find(text=soup_selected.get_text()).findNext("a").get("href")
    return next_page


def scrape_job_portal(webaddress="http://www.jobportal.com/link-to-first-page-of-job-list", options="--headless",
                     sleeptime=3, to_log=""):
    '''
    The main crawler program, connects to the page and scrapes the list of jobs. Uses the _find_next_page function to
    navigate the list pages. Records the following info from every job: vacancy name, full internet address to its page,
    date of scraping, time of scraping, text contents of ad.
    date of scraping, time of scraping, text contents of ad.

    After collection of all job vacancy's addresses, this program initiates the scraping of every address (through
    program PP_scrape_linklist below). Returns time of operation and 3 lists: the list of text content for every
    individual job ad (see program _scrape_linklist), list of info from listed ads and list of jobs that were not
    scraped successfully.

    :param webaddress: internet address to the first page of the job list that has to be scraped
    :param options: various options to the simulation browser; the default is '--headless' which will open the browser
        in the background
    :param sleeptime: the time interval between each connection to the website; the default is 3 seconds
    :param to_log: path to the file that is wished to be used as the log; the default is an empty path, which means no
        log will be recorded
    :return: information about recorded job ads, failed scrapings and time spent executing process
    '''
    start = time.time()
    if to_log:
        with open(to_log, "w+", encoding="utf8") as logfile:
            sys.stdout = logfile
            print("Starting scraping JobPortal at datetime %s\n\tStarting link: %s"
                  %(time.strftime("%d.%m.%Y %H:%M:%S"), webaddress))
            sys.stdout = sys.__stdout__
    # Open page (through proxy)
    prox = url.ProxyHandler({"https": "http://proxy_address:port"})
    opener = url.build_opener(prox)
    url.install_opener(opener)
    html = url.urlopen(webaddress)
    soup = BeautifulSoup(html, "html.parser")
    JVnum = []
    JVs = []
    i = 0
    boxes = []
    breaking = False
    print("Finding vacancies.", end="")
    sys.stdout.flush()
    # While there is a next page, search and record job vacancies.
    while _find_next_page(soup):
        time.sleep(3)
        if to_log:
            with open(to_log, "a", encoding="utf8") as logfile:
                sys.stdout = logfile
                print(time.strftime("%d.%m.%Y %H:%M:%S") + "\tNew next page found:", _find_next_page(soup))
                sys.stdout = sys.__stdout__
        try:
            JVs_on_page = []
            # There may be more than one class of ads (i.e. 'silver' and 'gold' customers of the job portal) and their
            # ads may be different in appearance and HTML structure. This is why we might need multiple scraping loops. 
            for box in soup.find_all("div", {"class": re.compile("vacancy")}):
                href = "http://www.jobportal.com/" + box.find("a").get("href")
                JVs_on_page.append(href)
                info = [box.find("h2", {"class": "title"}).get_text(), href, datetime.today().strftime("%d.%m.%Y"),
                        datetime.today().strftime("%H:%M")]
                for tags in box.find_all("div", {"class": "ad-content gold"}):
                    info.append(tags.find("div", {"class": "details"}).get_text())
                boxes.append(info)
            for box in soup.find_all("a", {"class": re.compile("vacancy")}):
                JVs_on_page.append("http://www.jobportal.com/" + box.get("href"))
                info = [box.find("li", {"class": "title"}).get_text(), "http://www.jobportal.com/" + box.get("href"),
                        datetime.today().strftime("%d.%m.%Y"), datetime.today().strftime("%H:%M")]
                for tags in box.find("div", {"class": "ad-content silver"}):
                    info.append(tags.find("div", {"class": "details"}).get_text())
                boxes.append(info)
            JVs.extend(JVs_on_page)
            JVnum.append(len(JVs_on_page))
            # Connect to the next page
            html = url.urlopen("https://www.jobportal.com/" + _find_next_page(soup))
            soup = BeautifulSoup(html, "html.parser")
            i += 1
            print(".", end="")
            sys.stdout.flush()
        except KeyboardInterrupt:  # In the event that we need to stop the process, this interrupts it cleanly
            if to_log:
                with open(to_log, "a", encoding="utf8") as logfile:
                    sys.stdout = logfile
                    print("Vacancies list scraping interrupted at datetime %s" %time.strftime("%d.%m.%Y %H:%M:%S"))
                    sys.stdout = sys.__stdout__
            breaking = True
            print("\nOperation was interrupted!")
            sys.stdout.flush()
            break
    # Execute scraping one last time on the last page.
    if not breaking:
        JVs_on_page = []
        for box in soup.find_all("div", {"class": re.compile("vacancy")}):
            href = "http://www.jobportal.com/" + box.find("a").get("href")
            JVs_on_page.append(href)
            info = [box.find("h2", {"class": "title"}).get_text(), href, datetime.today().strftime("%d.%m.%Y"),
                    datetime.today().strftime("%H:%M")]
            for tags in box.find_all("div", {"class": "ad-content gold"}):
                info.append(tags.find("div", {"class": "details"}).get_text())
            boxes.append(info)
        for box in soup.find_all("a", {"class": re.compile("vacancy")}):
            JVs_on_page.append("http://www.jobportal.com/" + box.get("href"))
            info = [box.find("li", {"class": "title"}).get_text(), "http://www.jobportal.com/" + box.get("href"),
                    datetime.today().strftime("%d.%m.%Y"), datetime.today().strftime("%H:%M")]
            for tags in box.find("div", {"class": "ad-content silver"}):
                info.append(tags.find("div", {"class": "details"}).get_text())
            boxes.append(info)
        JVs.extend(JVs_on_page)
        JVnum.append(len(JVs_on_page))
        print(".", end="")
        sys.stdout.flush()
    print()
    sys.stdout.flush()
    time_elapsed = (time.time() - start)
    print("Time elapsed for link gathering: %dm %ds" % (time_elapsed // 60, time_elapsed % 60))
    print("Starting scraping list of sites!")
    sys.stdout.flush()
    if to_log:
        with open(to_log, "a", encoding="utf8") as logfile:
            sys.stdout = logfile
            print("Vacancies list scraping ended at datetime %s. Time elapsed %dm %ds"
                  % (time.strftime("%d.%m.%Y %H:%M:%S"), time_elapsed // 60, time_elapsed % 60))
            sys.stdout = sys.__stdout__
    # Scrape individual ads, sorts the job ads' info and individual ads' info according to the current internet address.
    scrap = PP_scrape_linklist(JVs, options, sleeptime=sleeptime, to_log=to_log)
    boxes = sorted(boxes, key=lambda element: (element[1], element))
    scrap = sorted(scrap)
    failed_JVs = [col[0] for col in scrap if col[2] == "THIS LINK COULD NOT BE REACHED!"]
    return scrap, boxes, failed_JVs, time_elapsed


def scrape_sites(scrap, boxes, failed_JVs, time_elapsed, options="--headless", sleeptime=3, to_csv="", to_log=""):
    '''
    This program matches scraped job ads information with their individual pages' content. If the parameter 'to_csv' is
    not and empty string, then the results are saved to a csv file on the path given by the parameter. Returns job ads
    with their matched text contents.

    The csv file has the following columns:
        "VacancyPost", "LinkToJV", "ScrapeDate", "ScrapeTime", "PostDate", "VacancySite",, "SourceLink" and "Content"
    * Note: different columns may be present on different job portals.

    :param scrap: list of all scraped content for all ads
    :param boxes: list of info about every job ad
    :param failed_JVs: list of ads that were not scraped successully
    :param time_elapsed: time needed for the operation
    :param options: various options to the simulation browser; the default is '--headless' which will open the browser
        in the background
    :param sleeptime: the time interval between each connection to the website; the default is 3 seconds
    :param to_csv: path to the file that is wished to be used as information records; the default is an empty path,
        which means no such file is created
    :param to_log: path to the file that is wished to be used as the log; the default is an empty path, which means no
        log will be recorded
    :return: a list of information about every job ad including their individual text content
    '''
    start = time.time()
    if to_log:
        with open(to_log, "a", encoding="utf8") as logfile:
            sys.stdout = logfile
            print("Results of scraping:\n\t\t- number of scraped items: %d\n\t\t" % len(scrap) +
                  "- number of job boxes: %d\n\t\t- number of failed links: %d" % (len(boxes), len(failed_JVs)))
            sys.stdout = sys.__stdout__
    # Retries to scrape failed job vacancies
    if failed_JVs:
        if to_log:
            with open(to_log, "a", encoding="utf8") as logfile:
                sys.stdout = logfile
                print("Starting scraping failed links from JobPortal at %s" % time.strftime("%d.%m.%Y %H:%M:%S"))
                sys.stdout = sys.__stdout__
            to_log_failed = to_log[:-4] + "_failed.txt"
        else:
            to_log_failed = ""
        scrap_failed = PP_scrape_linklist(failed_JVs, options, sleeptime=sleeptime, to_log=to_log_failed)
        for row in scrap_failed:
            scrap[[i[0] for i in scrap].index(row[0])][2] = row[2]
        if to_log:
            with open(to_log, "a", encoding="utf8") as logfile:
                with open(to_log_failed, "r", encoding="utf8") as logfail:
                    log = logfail.readlines()
                ordered_logs = sorted(log, key=lambda word: (word[:19], word))
                logfile.writelines(ordered_logs)
            os.remove(to_log[:-4] + "_failed.txt")
    for n, row in enumerate(boxes):
        if row[1] != scrap[n][0]:  # It is possible due to unforseen circumstances that some ads don't have a matching
            if to_log:             # text content item. We skip these ads.
                with open(to_log, "a", encoding="utf8") as logfile:
                    sys.stdout = logfile
                    print("%s: UNMATCHED ELEMENTS %d!:\n\t%s \n\t%s"
                          % (time.strftime("%d.%m.%Y %H:%M:%S"), n, row[1], scrap[n][0]))
                    sys.stdout = sys.__stdout__
            print("UNMATCHED ELEMENTS %d!:\n%s \n%s" % (n, row[1], scrap[n][0]))
            sys.stdout.flush()
            continue
        row.extend([scrap[n][1], scrap[n][2]])
    # Results are saved to the csv file if parameter 'to_csv' is given
    if to_csv:
        if to_log:
            with open(to_log, "a", encoding="utf8") as logfile:
                sys.stdout = logfile
                print("Saving content to csv file: %s" % to_csv)
                sys.stdout = sys.__stdout__
        csv_boxes = boxes.copy()
        for row in csv_boxes:
            row[9] = row[9].replace("\n", "\\n").replace("\t", "\\t")
        with open(to_csv, "w+", newline="", encoding="utf-8") as cs:
            writ = csv.writer(cs)
            writ.writerows([["VacancyPost", "LinkToJV", "ScrapeDate", "ScrapeTime", "PostDate", "Firm", "VacancySite",
                            "Sex", "SourceLink", "Content"]])
            writ.writerows(csv_boxes)
        del csv_boxes
    time_elapsed = (time.time() - start) + time_elapsed
    if to_log:
        with open(to_log, "a", encoding="utf8") as logfile:
            sys.stdout = logfile
            print("Operation completed at datetime %s. Time elapsed %dm %ds."
                  % (time.strftime("%d.%m.%Y %H:%M:%S"), time_elapsed // 60, time_elapsed % 60))
            sys.stdout = sys.__stdout__
    print("Time elapsed for the process of scraping sites: %dm %ds" % (time_elapsed // 60, time_elapsed % 60))
    sys.stdout.flush()
    return boxes


def PP_scrape_linklist(JVs, options, sleeptime, to_log):
    '''
    This program handles the opening and closing of 3 thread-processes which are used for parallel scraping. Each
    process opens its own Firefox simulation browser to scrape the pages. The scrapes are returned together as a list.

    :param JVs: list of all job vacancy ads to be scraped
    :param options: various options to the simulation browser; the default is '--headless' which will open the browser
        in the background
    :param sleeptime: the time interval between each connection to the website; the default is 3 seconds
    :param to_log: path to the file that is wished to be used as the log; the default is an empty path, which means no
        log will be recorded
    :return: joint list of results from each process
    '''
    results = []
    unbreaking = True
    if len(JVs) >= 3:  # If the number of items to be scraped is higher than 3 the list is divided in 3 quasi-equal
                       # parts and fed to the program _qscrape_linklist in 3 threads.
        JVs1, JVs2, JVs3 = [JVs[i:(i+(len(JVs) // 3))] for i in range(0, (len(JVs) // 3)*3, len(JVs) // 3)]
        q = Queue()
        # 3 processes are created, each executing the program _qscrape_linklist with their sublist
        p1 = Process(target=_qscrape_linklist, args=(q, JVs1, options, sleeptime, "1", to_log[:-4] + "1.txt"))
        p2 = Process(target=_qscrape_linklist, args=(q, JVs2, options, sleeptime, "2", to_log[:-4] + "2.txt"))
        p3 = Process(target=_qscrape_linklist, args=(q, JVs3, options, sleeptime, "3", to_log[:-4] + "3.txt"))
        # The processes are started
        p1.start()
        p2.start()
        p3.start()
        # Unless a manual stop is given the results are joined
        try:
            for k in range(3):
                results.extend(q.get(True))
        except KeyboardInterrupt:
            unbreaking = False
            signal.CTRL_C_EVENT
            if to_log:
                with open(to_log, "a", encoding="utf8") as logfile:
                    sys.stdout = logfile
                    print(time.strftime("%d.%m.%Y %H:%M:%S"),": MANUAL INTERRUPTION OF SCRAPING!")
                    sys.stdout = sys.__stdout__
            print("\nScraping was manually interrupted.")
            sys.stdout.flush()
            # if manual stop is given the current processes' results are joined and then the processes are terminated.
            for k in range(3):
                results.extend(q.get(True))
            p1.terminate()
            p2.terminate()
            p3.terminate()
        # No matter how the processes are stopped, they threads are joined at the end and the lists are deleted.
        finally:
            p1.join()
            p2.join()
            p3.join()
        del JVs1, JVs2, JVs3
        if to_log:
            with open(to_log, "a", encoding="utf8") as logfile:
                with open(to_log[:-4] + "1.txt", "r") as logfile1:
                    log1 = logfile1.readlines()
                with open(to_log[:-4] + "2.txt", "r") as logfile2:
                    log2 = logfile2.readlines()
                with open(to_log[:-4] + "3.txt", "r") as logfile3:
                    log3 = logfile3.readlines()
                ordered_logs = sorted(log1 + log2 + log3, key=lambda word: (word[:19], word))
                logfile.writelines(ordered_logs)
            # If logs are being written, then the auxiliary logs from each process are joined into next one and deleted.
            os.remove(to_log[:-4] + "1.txt")
            os.remove(to_log[:-4] + "2.txt")
            os.remove(to_log[:-4] + "3.txt")
    if unbreaking and (len(JVs) - len(JVs) % 3) < len(JVs):
        # If the number of items to be scraped is lower than 3, then only one process/thread is used.
        results.extend(_scrape_linklist(JVs[(len(JVs) - len(JVs) % 3):], options, sleeptime, "$", to_log))
    return results


def _scrape_linklist(lst, options, sleeptime, th, to_log):
    '''
    This is a program that scrapes the content from individual job ad pages. It starts a Firefox simulation browser,
    connects to given page and scrapes its text contents. It returns a list of all job ads fed in the following format:
    vacancy name, job ad address, text content.

    :param lst: list of job ads' addresses to be scraped
    :param options: various options to the simulation browser; the default is '--headless' which will open the browser
        in the background
    :param sleeptime: the time interval between each connection to the website; the default is 3 seconds
    :param th: index of the current thread for logging purposes
    :param to_log: path to the file that is wished to be used as the log; the default is an empty path, which means no
        log will be recorded
    :return: a list of scraped information for every job ad
    '''
    browser_options = Options()
    if isinstance(options, str):
        options = [options]
    elif isinstance(options, list) and all(map(lambda x: isinstance(x, str), options)):
        pass
    else:
        raise TypeError("\'options\' parameter needs to be either str or list of str!")
    if options[0]:
        for op in options:
            browser_options.add_argument(op)
    # The program starts a Firefox simulation browsers. See document Scrape.doc for more info.
    bins = FirefoxBinary("\\PATH\\TO\\FIREFOX\\BINARY\\DIR\\firefox.exe")
    driver = webdriver.Firefox(executable_path="\\PATH\\TO\\GECKODRIVER\\EXECUTABLE\\DIR\\geckodriver.exe",
                               firefox_binary=bins, firefox_options=browser_options,
                               log_path="\\PATH\\TO\\GECKODRIVER\\LOGS\\DIRECTORY\\geckodriver_log%s.txt" % th)
    jobs = []
    for n, link in enumerate(lst):
        time.sleep(sleeptime)
        try:
            driver.set_page_load_timeout(10)  # Hardcoded load time of each page
            try:
                driver.get(link)
            except TimeoutException:
                try:
                    driver.refresh()  # We retry once if the page didn't load in time
                except TimeoutException:
                    print("Link %d on driver %s (%s) could not be reached!" % (n, th, link))
                    sys.stdout.flush()
                    jobs.append([link, driver.current_url, "THIS LINK COULD NOT BE REACHED!"])
                    if to_log:
                        with open(to_log, "a+", encoding="utf8") as logfile:
                            sys.stdout = logfile
                            print("%s: Link %d on driver %s (%s) could not be reached!"
                                  % (time.strftime("%d.%m.%Y %H:%M:%S"), n, th, link))
                            sys.stdout = sys.__stdout__
                    continue
            time.sleep(2)
            job_soup = BeautifulSoup(driver.page_source, "html.parser")
            text = job_soup.find("div", {"class": "job-description"})
            if not text:
                jobs.append([link, driver.current_url, ""])
            else:
                jobs.append([link, driver.current_url, text.get_text()])
            print("Driver", th, ", link no.", n, ":", link)
            sys.stdout.flush()
            if to_log:
                with open(to_log, "a+", encoding="utf8") as logfile:
                    sys.stdout = logfile
                    print(time.strftime("%d.%m.%Y %H:%M:%S")+ "\tDriver", th, ", link no.", n, ":", link)
                    sys.stdout = sys.__stdout__
        except KeyboardInterrupt:  # Manual interruption closes the driver cleanly
            if to_log:
                with open(to_log, "a+", encoding="utf8") as logfile:
                    sys.stdout = logfile
                    print(time.strftime("%d.%m.%Y %H:%M:%S"),": MANUAL INTERRUPTION OF SCRAPING!")
                    sys.stdout = sys.__stdout__
            print("Manual interruption of driver %s in progress!" % th)
            sys.stdout.flush()
            driver.quit()
            break
    driver.quit()
    return jobs


def _qscrape_linklist(queue, lst, options, sleeptime, th, to_log):
    '''
    This is an auxiliary function that puts returns queued results of each process that is ran in parallel. Each process
    runs an instance of the _scrape_linklist program.

    :param lst: list of job ads' addresses to be scraped
    :param options: various options to the simulation browser; the default is '--headless' which will open the browser
        in the background
    :param sleeptime: the time interval between each connection to the website; the default is 3 seconds
    :param th: index of the current thread for logging purposes
    :param to_log: path to the file that is wished to be used as the log; the default is an empty path, which means no
        log will be recorded
    :return: a queued list of scraped information for every job ad
    '''
    return queue.put(_scrape_linklist(lst, options, sleeptime, th, to_log))
