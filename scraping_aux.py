#!/usr/bin/env bash
# -*- coding: utf-8 -*-
import csv  # .csv functionality
import xlrd  # Excel files opening
import xlwt  # Excel files writing
import sys  # Module with additional system tools
import os  # Module with tools for working with files and folders
from selenium.webdriver.firefox.webelement import FirefoxWebElement  # Firefox browser elements functionality
from selenium.webdriver.remote.webelement import WebElement  # Non-Firefox browser elements functionality
from datetime import datetime, timedelta  # Date and time functionality and operations
from time import sleep  # Pausing python
from selenium.common.exceptions import StaleElementReferenceException  # Dealing with errors in changing pages

# Win10 fix for printing into a custom stdout (e.g. logfile)
import win_unicode_console
win_unicode_console.enable()


def check_previous_links(domain_name, archive_dir, other_chs=None):
    """Checks previously scraped files to avoid duplicated scraping; it is supposed these files are in .csv format"""
    previous_files = [file for file in os.listdir(archive_dir) if
                      domain_name.lower() in file.lower() and file.endswith("csv") and not file.startswith("JSON")]
    other_chs = [] if other_chs is None else other_chs
    if isinstance(other_chs, str):
        other_chs = [other_chs]
    if other_chs:
        previous_files = [file for file in previous_files if all(map(lambda x: x.lower() in file.lower(), other_chs))]
    previous_links = []
    for file in previous_files:
        with open(os.path.join(archive_dir, file), "r", encoding="utf8") as article_links:
            reader = csv.reader(article_links, delimiter=";")
            articles = [row[0] for row in reader][1:]
        previous_links.extend(articles)
    return previous_links


def schedule_scraping(module, dateandtime=""):
    if dateandtime == "":
        dateandtime = datetime.fromtimestamp(datetime.now().timestamp() - 60).strftime("%d.%m.%Y/%H:%M")
    elif datetime.strptime(dateandtime, "%d.%m.%Y/%H:%M") < datetime.now():
        raise ValueError("Second argument must be a time in the future...")
    if "." not in module:
        print("\n\nParameter module is incomplete!!")
        return
    sys.path.insert(0, module[:module.index(".")])
    module = __import__(module[module.index(".") + 1:])
    print(module)
    k = 0
    while datetime.strptime(dateandtime, "%d.%m.%Y/%H:%M") > datetime.now():
        print("\rNow waiting for time %s %s" % (dateandtime, "." * (k % 4) + " " * (3 - k % 4)), end="")
        sys.stdout.flush()
        sleep(1)
        k += 1
    print("")
    module.main()


def send_buttons(driver_, xpath, keys=None, pos=0):
    """Button pressing in browser elements"""
    if isinstance(xpath, (FirefoxWebElement, WebElement)):
        el = xpath
    else:
        try:
            el = driver_.driver.find_elements_by_xpath(xpath)[pos]
        except StaleElementReferenceException:
            sleep(0.1)
            el = driver_.driver.find_elements_by_xpath(xpath)[pos]
    if keys is None:
        driver_.driver.execute_script("arguments[0].click();", el)
    else:
        if isinstance(keys, str):
            sleep(0.5)
            el.send_keys(keys[0])
            k = 1
            while k < len(keys):
                try:
                    el = driver_.driver.find_elements_by_xpath(xpath)[pos]
                    el.send_keys(keys[k])
                except StaleElementReferenceException:
                    sleep(0.1)
                    el = driver_.driver.find_elements_by_xpath(xpath)[pos]
                    el.send_keys(keys[k])
                sleep(0.05)
                k += 1
        else:
            el.send_keys(keys)


def numbers_report(lst, save_dir, date_format="%d.%m.%Y"):
    """Save number of recorded articles"""
    comma = True
    try:
        with open(save_dir, "r+") as report:
            rep = report.readlines()
    except FileNotFoundError:
        rep = ["\n", ""]
        comma = False
    rep[0] = rep[0].replace("\n", "," * comma + datetime.now().strftime(date_format) + "\n")
    rep[1] += "," * comma + "%d" % len(lst)
    with open(save_dir, "w+") as report:
        report.writelines(rep)


def next_monday(date, day=0):
    """Returns the date of the following monday (or any other day) given a date"""
    date += timedelta(days=(1 if date.weekday() == day else 0) - day)
    return date + timedelta(days=(-date.weekday() + 7) % 7 + day)


if __name__ == "__main__":
    schedule_scraping(sys.argv[1], sys.argv[2])
