#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=UTF-8

# This library holds the program check_scrapes which is used to check the quality of scraped job vacancies tables.

from datetime import datetime  # formatting dates
from ctypes import windll  # creating Windows Message/Error boxes
import csv  # reading and writing csv files
import sys  # system-specific parameters and functions


def check_scrapes(JP, datum=str(datetime.now().strftime("%Y-%m-%d")), to_log=""):
    '''
    This program checks the tables that result from scraping job vacancies. Firstly it checks if the date is in the
    right format, if the table exists, if it opens and if it holds any information. Depending on the Job Portal it
    checks the number and names of the columns and the format of all values in the date and time columns.

    :param JP: name of Job Portal
    :param datum: the date against which the scraping dates are checked, absolutely in the YEAR-MM-DD format;
        the default date is the date of running
    :param to_log: the path to the file of the log, if it exists; the default is an empty string which means no log file
    :return: a Windows popup notification window with either errors listed or a message that everything concluded
        correctly
    '''
    try:
        datum = datetime.strptime(datum, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return windll.user32.MessageBoxW(0, "Entered date not in the right format: \"%s\"." % datum, "WARNING", 0x30)
    checks = [False for _ in range(7)]
    try:
        with open("\\PATH\\TO\\JOBPORTAL\\TABLE\\table.csv", "r", encoding="utf8") as JPcsv:
            JPlst = [row for row in csv.reader(JPcsv)]
    except FileNotFoundError:
        return windll.user32.MessageBoxW(0, "table.csv DOES NOT EXIST!!", "WARNING", 0x30)
    except:
        return windll.user32.MessageBoxW(0,
                                         "table.csv DID NOT OPEN CORRECTLY BECAUSE OF AN UNKNOWN ERROR!", "WARNING", 0)
    if len(JPlst) == 0 or (len(JPlst) == 1 and len(JPlst[0]) == 1):
        if to_log:
            with open(to_log, "a+") as logfile:
                sys.stdout = logfile
                print("Errors are present:\n - the file is empty!")
                sys.stdout = sys.__stdout__
        return windll.user32.MessageBoxW(0, "table.csv IS EMPTY!", "WARNING", 0x10)
    # The names of the columns depend on the job portal.
    if (JP == "JobPortal1" and all(i in JPlst[0] for i in ['VacancyPost', 'LinkToJV', 'ScrapeDate', 'ScrapeTime',
                                                         'PostDate', 'Firm', 'VacancySite', 'Sex', 'SourceLink',
                                                         'Content'])) \
        or (JP == "JobPortal2" and all(i in JPlst[0] for i in ['VacancyPost', 'LinkToJV', 'ScrapeDate',
                                                                   'ScrapeTime', 'PostDate', 'Firm', 'VacancySite',
                                                                   'SourceLink', 'Content'])):
        checks[0] = True
    if all([len(i) == len(JPlst[0]) for i in JPlst[1:]]):
        checks[1] = True
    if all([row[2] == datetime.strptime(datum, "%Y-%m-%d").strftime('%d.%m.%Y') for row in JPlst[1:]]):
        checks[2] = True
    try:
        for row in JPlst[1:]:
            datetime.strptime(row[3], "%H:%M")
    except ValueError:
        pass
    else:
        checks[3] = True
    try:
        for row in JPlst[1:]:
            datetime.strptime(row[4], "%d.%m.%Y")
    except ValueError:
        try:
            for row in JPlst[1:]:
                datetime.strptime(row[5][-11:-1], "%d.%m.%Y")
        except ValueError:
            pass
        else:
            checks[5] = True
    else:
        checks[4] = True
        checks[5] = True
    # Is there a common presence of unwanted text?
    if not any([row[4].startswith("Unwanted text: ") for row in JPlst]) \
            and not any(["Unwanted text" in row[6] for row in JPlst]):
        checks[6] = True
    if not all(checks):
        errs_EN = [" - Errors in column names", " - Errors in row lengths", " - Errors in scraping date",
                   " - Error in time format", " - Possible errors in the order of columns \"PostDate\" and \"Firm\"",
                   " - Error in published date format", " - Errors in unneeded strings"]
        chosen_errs_EN = "\n".join([errs_EN[i] for i, j in enumerate(checks) if not j])
        message = "table.csv INCLUDES ERRORS:" + "\n" + chosen_errs_EN + "\n\n"
        if to_log:
            with open(to_log, "a+") as logfile:
                sys.stdout = logfile
                print("Errors are present:\n" + chosen_errs_EN)
                sys.stdout = sys.__stdout__
        return windll.user32.MessageBoxW(0, message, "WARNING", 0x10)
    else:
        if to_log:
            with open(to_log, "a+") as logfile:
                sys.stdout = logfile
                print("No errors were detected during checking. The scraping has concluded without errors.")
                sys.stdout = sys.__stdout__
        return windll.user32.MessageBoxW(0, "Scraping of table.csv has concluded correctly.", "MESSAGE", 0x40)
