#!/usr/bin/env bash
# -*- coding: utf-8 -*-
import csv  # delo s csv datotekami
import xlrd  # odpiranje Excel datotek
import xlwt  # pisanje v Excel datoteke
import sys  # ukazi sistemu (za vnašanje spremenljivk preko ukazne vrstice)
import os  # ukazi sistemu (za brisanje datotek)
from selenium.webdriver.firefox.webelement import FirefoxWebElement  # Delo na elementih v brskalnikih Firefox
from selenium.webdriver.remote.webelement import WebElement  # Delo na elementih v drugih brskalnikih
from datetime import datetime, timedelta
from time import sleep
from platform import system
from selenium.common.exceptions import StaleElementReferenceException

# Win10 fix za printanje v neklasičen stdout (recimo logfile)
import win_unicode_console
win_unicode_console.enable()


def check_previous_links(domain_name, archive_dir, other_chs=None):
    archive_dir = os_adapt(archive_dir)
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


def os_adapt(save_dir):
    if not save_dir:
        return save_dir
    if system() == "Linux" and not save_dir.startswith("/"):
        if save_dir == r"..\firefox.exe":  # Windows firefox path
            save_dir = "../firefox"  # Linux firefox path
        elif save_dir == r"..\chrome.exe":  # Windows firefox path
            save_dir = "../google-chrome"  # Linux firefox path
        else:
            # change windows format to linux format
            save_dir = ".." + save_dir.replace(":", "").replace("\\", "/").replace(".exe", "")
    if system() == "Windows" and save_dir.startswith("/"):
        if save_dir == "../firefox":  # Linux firefox path
            save_dir = r"..\firefox.exe"  # Windows firefox path
        elif save_dir == "../google-chrome":  # Linux firefox path
            save_dir = r"..\chrome.exe"  # Windows firefox path
        else:
            raise SystemError("File only exists on Linux system.")
        if "." not in save_dir[-5:]:
            save_dir += ".exe"
    return save_dir


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
    save_dir = os_adapt(save_dir)
    # Save number of recorded articles
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


def next_monday(date):
    date += timedelta(days=(1 if not date.weekday() else 0))
    return date + timedelta(days=(-date.weekday() + 7) % 7)


if __name__ == "__main__":
    schedule_scraping(sys.argv[1], sys.argv[2])
