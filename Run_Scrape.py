#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=UTF-8

# The launcher for the scraping process, can be called in Windows Task Scheduler with the following script and arguments
#   Script:     C:\Windows\System32\cmd.exe
#   Arguments:  /c Path:\To\Python\python "Path:\To\Run_Scrape.py"

from Scrape import scrape_job_portal, scrape_sites  # import the scraping functions from the custom-made Scrape library
from check_scrapes import check_scrapes  # import the check_scrapes function from the custom-made check_scrapes library
from time import strftime, sleep  # functions for formatting time and pausing execution of processes
from datetime import date, timedelta  # functions for handling and calculating with time objects
import sys, csv  # system-specific parameters and functions and reading and writing csv files


# If this file is run as a script start the following:
if __name__ == "__main__":
    scrap, boxes, failed_JVs, time_elapsed = scrape_job_portal(
        webaddress="http://www.jobportal.com/link-to-first-page-of-job-list",
        to_log="\\DIR\\TO\\TABLES\\JobPortal_log_%s.txt" % strftime("%Y-%m-%d"))

    print("Waiting 30 seconds.", end="")
    sys.stdout.flush()
    for _ in range(15):
        sleep(2)
        print(".", end="")
        sys.stdout.flush()
    print()
    sys.stdout.flush()
    JPs = scrape_sites(scrap, boxes, failed_JVs, time_elapsed,
                        to_log="\\DIR\\TO\\LOG\\JobPortal_log_%s.txt" % strftime("%Y-%m-%d"))
    # The job portal has recent dates in word form, we have to change that
    for item_list in JPs:
        if item_list[4] == "Yesterday":
            item_list[4] = (date.today() + timedelta(days=-1)).strftime("%d.%m.%Y")
        elif item_list[4] == "Today":
            item_list[4] = date.today().strftime("%d.%m.%Y")
        else:
            # The dates should be in dd.mm.YYYY form
            item_list[4] = ".".join(map(lambda el: el.zfill(2), item_list[4].split(".")))
        # Replacing some unwanted text in the text content column:
        if ("Unwanted_Start1" in item_list[9] or "Unwanted_Start2" in item_list[9]) and "Unwanted_end" in item_list[9]:
            one = (item_list[9].find("Unwanted_Start1") if item_list[9].find("Unwanted_Start1") > 0 else 99999999)
            two = (item_list[9].find("Unwanted_Start2") if item_list[9].find("Unwanted_Start2") > 0 else 99999999)
            item_list[9] = item_list[9].replace(item_list[9][
                                                min(one, two):len(item_list[9])
                                                              - item_list[9][::-1].index("Unwanted_End")
                                                ], "")
        # Replacing newlines and tab characters with spaces and stripping leading and ending spaces
        item_list[9] = item_list[9].replace("\n", " ").replace("\t", "    ").strip()
    # Save found job portal vacancies to a csv file.
    with open("\\DIR\\TO\\TABLES\\JobPortal_%s.txt" % strftime("%Y-%m-%d"), "w+", newline="", encoding="utf-8") as cs:
        writ = csv.writer(cs)
        writ.writerows([["VacancyPost", "LinkToJV", "ScrapeDate", "ScrapeTime", "PostDate", "Firm", "VacancySite",
                         "Sex", "SourceLink", "Content"]])
        writ.writerows(JPji)
    print("In 2 minutes a check of scraped items will be executed.")
    sleep(120)
    # Checking whether the scraping has concluded correctly
    check_scrapes("MojeDelo", to_log=True)
