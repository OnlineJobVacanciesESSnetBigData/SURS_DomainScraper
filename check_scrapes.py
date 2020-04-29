from tkinter import Tk, messagebox
import csv
from urllib.parse import urlparse
from datetime import datetime
from scraping_aux import os_adapt


def _message(title, message, seriousness=0):
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    if seriousness == 0:
        messagebox.showinfo(title, message)
    elif seriousness == 1:
        messagebox.showwarning(title, message)
    else:
        messagebox.showerror(title, message)
    root.destroy()


def check_comp(name, save_dir, res=None,
               date=datetime.now().strftime("%d-%m-%Y"), date_format="%d-%m-%Y", add_message=""):
    add_message = "\n\n" + add_message if add_message else ""
    res = list() if res is None else res
    # Files checks
    try:
        datetime.strptime(date, date_format)
    except ValueError:
        _message("WARNING", "Parameter \"date\" should be in \"%s\" format: \"%s\"." % (date_format, date), 1)
        return
    try:
        with open(os_adapt(save_dir + "\\%s_SEZNAM_%s.csv" % (name, date)), "r", encoding="utf8") as cs:
            comps = [row for row in csv.reader(cs, delimiter=";", quotechar="\"")]
    except FileNotFoundError:
        _message("ERROR", "%s_SEZNAM_%s.csv DOES NOT EXIST!!" % (name, date), 2)
        return
    except:
        _message("ERROR", "%s_SEZNAM_%s.csv CANT BE OPENED!!" % (name, date), 2)
        return
    try:
        with open(os_adapt(save_dir + "\\ARTICLES_%s_SEZNAM_%s.csv" % (name, date)), "r", encoding="utf8") as cs:
            arts = [row for row in csv.reader(cs, delimiter=";", quotechar="\"")]
    except FileNotFoundError:
        _message("ERROR", "ARTICLES_%s_SEZNAM_%s.csv DOES NOT EXIST!!" % (name, date), 2)
        return
    except:
        _message("ERROR", "ARTICLES_%s_SEZNAM_%s.csv CANT BE OPENED!!" % (name, date), 2)
        return
    if len(comps) == 0 or (len(comps) == 1 and len(comps[0]) == 1):
        _message("ERROR", "%s_SEZNAM_%s.csv IS EMPTY!!" % (comps, date), 2)
        return
    if len(arts) == 0 or (len(arts) == 1 and len(arts[0]) == 1):
        _message("ERROR", "ARTICLES_%s_SEZNAM_%s.csv IS EMPTY!!" % (comps, date), 2)
        return
    # Format checks
    checks = [True for _ in range(13)]
    if not comps[0] == ["naziv_izdelka", "naziv_izdelka_link", "cena",
                        "REQUEST_URL", "RESPONSE_URL", "RESPONSE_DATE", "RESPONSE_TIME"]:
        checks[0] = False
    if not arts[0] == ["naziv_izdelka_link", "RESPONSE_URL", "RESPONSE_DATE",
                       "RESPONSE_TIME", "ARTICLE_ID", "breadcrumbs", "DESCP"]:
        checks[1] = False
    if not (all([len(k) == len(comps[0]) for k in comps[1:]])):
        checks[2] = False
    if not (all([len(k) == len(arts[0]) for k in arts[1:]])):
        checks[3] = False
    try:
        all(datetime.strptime(row[6], "%H:%M:%S") for row in comps[1:])
    except ValueError:
        checks[4] = False
    try:
        all(datetime.strptime(row[5], "%d.%m.%Y") for row in comps[1:])
    except ValueError:
        checks[5] = False
    try:
        all(datetime.strptime(row[3], "%H:%M:%S") for row in arts[1:])
    except ValueError:
        checks[6] = False
    try:
        all(datetime.strptime(row[2], "%d.%m.%Y") for row in arts[1:])
    except ValueError:
        checks[7] = False
    no_price = []
    if not all(row[2] for row in comps):
        no_price = ([comps.index(row) for row in comps if not row[2]])
        checks[8] = False
    try:
        all(float(row[2].replace(",", ".")) for row in comps[1:] if row[2])
    except ValueError:
        checks[9] = False
    no_url_comps = []
    if not all(all(urlparse(row[1])[:2] + urlparse(row[3])[:2]) for row in comps[1:]):
        no_url_comps = [comps.index(row) for row in comps[1:] if not all(urlparse(row[1])[:2] + urlparse(row[3])[:2])]
        checks[10] = False
    no_url_arts = []
    if not all(all(urlparse(row[0])[:2] + urlparse(row[1])[:2]) for row in arts[1:]):
        no_url_arts = [arts.index(row) for row in arts[1:] if not all(urlparse(row[0])[:2] + urlparse(row[1])[:2])]
        checks[11] = False
    if not set([l[0] for l in arts]).issubset([l[1] for l in comps]):
        checks[12] = False
    if not all(checks):
        errs = ["  - Variables in file %s_SEZNAM_%s.csv do not match the required form" % (name, date),              # 0
                "  - Variables in file ARTICLES_%s_SEZNAM_%s.csv do not match the required form" % (name, date),     # 1
                "  - Number of variables in %s_SEZNAM_%s.csv is not constant" % (name, date),                        # 2
                "  - Number of variables in ARTICLES_%s_SEZNAM_%s.csv is not constant" % (name, date),               # 3
                "  - Time variable in %s_SEZNAM_%s.csv is not in the right format" % (name, date),                   # 4
                "  - Date variable in %s_SEZNAM_%s.csv is not in the right format" % (name, date),                   # 5
                "  - Time variable in ARTICLES_%s_SEZNAM_%s.csv is not in the right format" % (name, date),          # 6
                "  - Date variable in ARTICLES_%s_SEZNAM_%s.csv is not in the right format" % (name, date),          # 7
                "  - Some articles in %s_SEZNAM_%s.csv do not have prices: %s"                                       # 8
                % (name, date, ", ".join(map(lambda x: str(x), no_price if len(no_price) < 6
                   else no_price[:5] + ["..."]))),
                "  - Prices variable in %s_SEZNAM_%s.csv is not in the right format" % (name, date),                 # 9
                "  - URL addresses variables in %s_SEZNAM_%s.csv are not in the right format. Rows: %s"             # 10
                % (name, date, ", ".join(map(lambda x: str(x), no_url_comps if len(no_url_comps) < 6
                   else no_url_comps[:5] + ["..."]))),
                "  - URL addresses variables in ARTICLES_%s_SEZNAM_%s.csv are not in the right format. Rows: %s"    # 11
                % (name, date, ", ".join(map(lambda x: str(x), no_url_arts if len(no_url_arts) < 6
                   else no_url_arts[:5] + ["..."]))),
                "  - URLs in ARTICLES_%s_SEZNAM_%s.csv are not subset of URLs in %s_SEZNAM_%s.csv"                  # 12
                % (name, date, name, date)]
        chosen_errs = "\n".join([errs[i] for i, j in enumerate(checks) if not j])
        message = "Errors are present in %s file(s):\n%s" % (name, chosen_errs)
        _message("WARNING", message + add_message, 1)
        return
    else:
        if res:
            _message("MESSAGE", "No errors were detected during checkup of %s files, scraping concluded.\n"
                                "\nFound items:      %d\nNew items:        %d\n"
                                "Difference:       %d\nScraped articles: %d"
                     % (name, len(res[0]), len(res[0]) - res[2], res[2], len(res[1])) + add_message)
        else:
            _message("MESSAGE", "No errors were detected during checkup of %s files.\n" % name + add_message)
        return


if __name__ == "__main__":
    import sys
    dir = "Q:\\CEMODE_projekt\\Web scraping\\Strgani_podatki\\" + sys.argv[2]
    dat = datetime.now().strftime("%YM%m") if not sys.argv[3] else sys.argv[3]
    dateformat = "%d-%m-%Y" if "-" in dat else ("%YM%m" if "M" in dat else "%d.%m.%Y")
    check_comp(sys.argv[1].upper(), dir, [], dat, dateformat)
