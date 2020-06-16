#!/usr/bin/env bash
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup  # HTML navigation
from selenium import webdriver  # Browser simulated scraping
from selenium.webdriver.firefox.options import Options  # Options for the Firefox browser simulation
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary  # Initialization for the browser
import sys  # Folder and file manipulation
from datetime import datetime  # Date and time manipulation
from urllib.parse import urlparse  # Parsing internet addresses
from warnings import warn  # Python warning mechanics
import re  # Regular expressions

from selenium.common.exceptions import TimeoutException  # Timeout exception handling
from selenium.common.exceptions import WebDriverException  # Unconnected internet sites' errors handling

# The following modules are used for browser simulation state monitoring
import http.client
import socket
from urllib3.exceptions import MaxRetryError
from selenium.webdriver.remote.command import Command

# Win10 fix for custom stdout printing (e.g. a logfile)
import win_unicode_console
win_unicode_console.enable()


class Driver(object):
    """Custom driver class, which opens and operates on a proxy Firefox browser."""
    driver = None
    current_url = None
    soup = BeautifulSoup("", "lxml")
    http = ""
    domain = ""
    path = ""
    params = ""
    query = ""
    fragment = ""
    n = 15
    meta = dict()
    __fresh__ = True

    def __init__(self, options=None, restrictions=None, to_log="", proxy_port=None, profile=None,
                 executable_path=None, bins_path=None, name="cstmdr", n=15, user_agent_string=None):
        """Initiate a Driver class object. """
        self.name = name
        self.n = n
        self.user_agent_string = "custombot" if user_agent_string is None \
            else user_agent_string
        if executable_path is None:
            executable_path = r"..\geckodriver.exe"  # Enter the path to the geckodriver executable
        if bins_path is None:
            bins_path = r"..\Firefox\firefox.exe"  # Enter the path to the Firefox browser executable
        if options is None:
            self.options = ["--headless"]
        else:
            self.options = options
        self.executable_path = executable_path
        self.bins_path = bins_path
        self.to_log = to_log if to_log else ""
        self.__change_restrictions__ = False if restrictions is not None else True
        self.restrictions = restrictions
        self.profile = profile
        if proxy_port is None:
            self.proxy_port = ("", 0) * 5
        else:
            self.proxy_port = proxy_port
        self.save_to_log("Opening new driver instance with the following options: %s" % self.options)

    def save_to_log(self, message, nblank=0, **kwargs):
        """Prints a message to the output screen and to the log if it is given"""
        print(u"%s%s" % ("\n"*nblank, message))
        if self.to_log:
            with open(self.to_log, "a", encoding="utf8") as logfile:
                sys.stdout = logfile
                print("%s%s:\t%s" % ("\n"*nblank, datetime.now().strftime("%d.%m.%Y %H:%M:%S"), message), **kwargs)
                sys.stdout = sys.__stdout__

    def get(self, link=None, n=None, webdriver_log="", timeout=None, th=""):
        """Connects to a internet link with a Firefox webdriver proxy browser.
         If such a proxy does not yet exist, it creates one"""
        self.__fresh__ = False
        soup = self.soup
        timeout = 20 if timeout is None else timeout
        if self.driver is None or not self.is_alive():
            if webdriver_log is None:
                pass
            elif not webdriver_log:
                # Enter a desirable path for the logfile
                webdriver_log = r"..\log_%s.log" % datetime.now().strftime("%d-%m-%Y_%H-%M")
            else:
                pass
            options = Options()
            for option in self.options:
                options.add_argument(option)
            profile = webdriver.FirefoxProfile()
            if self.profile is None:
                profile.set_preference("general.useragent.override", self.user_agent_string)
            else:
                for k, v in self.profile.items():
                    profile.set_preference(k, v)
            if not self.proxy_port:
                profile.set_preference("network.proxy.type", 5)
            elif not all(self.proxy_port):
                profile.set_preference("network.proxy.type", 0)
            else:
                profile.set_preference("network.proxy.type", 1)
                profile.set_preference("network.proxy.http", self.proxy_port[0])
                profile.set_preference("network.proxy.http_port", self.proxy_port[1])
                profile.set_preference("network.proxy.https", self.proxy_port[2])
                profile.set_preference("network.proxy.https_port", self.proxy_port[3])
                profile.set_preference("network.proxy.ssl", self.proxy_port[4])
                profile.set_preference("network.proxy.ssl_port", self.proxy_port[5])
                profile.set_preference("network.proxy.ftp", self.proxy_port[6])
                profile.set_preference("network.proxy.ftp_port", self.proxy_port[7])
                profile.set_preference("network.proxy.socks", self.proxy_port[8])
                profile.set_preference("network.proxy.socks_port", self.proxy_port[9])
            profile.set_preference("javascript.enabled", True)
            profile.update_preferences()
            self.save_to_log("New Firefox instance opening...")
            self.driver = webdriver.Firefox(executable_path=self.executable_path, options=options,
                                            firefox_binary=FirefoxBinary(self.bins_path), firefox_profile=profile,
                                            service_log_path=webdriver_log)
        self.driver.set_page_load_timeout(timeout)
        link = "about:blank" if link is None else link
        if urlparse(link).netloc != self.domain and self.__change_restrictions__:
            self.restrictions = None
        self.http, self.domain, self.path, self.params, self.query, self.fragment = urlparse(link)[:]
        self.current_url = link
        if link != "about:blank" and self.restrictions is None:
            self.check_robots(n=2, **{".call": True})
        if self.robots_deny(link=link):
            self.save_to_log("Driver %s: Robots deny access to this page (condition \'%s\')!"
                             % (self.name, self.robots_deny()))
            warn("Robots deny access to page(condition \'%s\', page \'%s\')!" % (self.robots_deny(), self.current_url))
            return False
        k = 0
        refresh = False
        while k < (self.n if n is None else n):
            try:
                if link == self.driver.current_url:
                    self.driver.refresh()
                    refresh = True
                else:
                    self.driver.get(link)
                break
            except TimeoutException:
                if th:
                    indx = str(k + 1) + " on driver %s" % th
                else:
                    indx = str(k + 1)
                self.save_to_log("(%s) TimeoutException on link %s, retrying" % (indx, link))
                k += 1
            except WebDriverException as e:
                self.save_to_log("Link %s could not be reached due to error %s" % (link, e))
                return False
        else:
            self.save_to_log("Link %s may not have been reached due to too many tries (%d)!"
                             % (link, self.n if n is None else n))
            self.driver.implicitly_wait(20)
            self.driver.execute_script("window.stop();")
        if refresh or BeautifulSoup(self.driver.page_source, "lxml") != soup:
            self.soup = BeautifulSoup(self.driver.page_source, "lxml")
            return True
        else:
            return False

    def resoup(self):
        """Reloads the Driver's soup attribute"""
        self.soup = BeautifulSoup(self.driver.page_source, "lxml")

    def complete_link(self, link=""):
        """Completes given link with the protocol and netloc prefix. Works only for HTTP and HTTPS protocols."""
        if not link:
            link = "://".join([self.http, self.domain])
        elif link.startswith("/"):
            link = "://".join([self.http, self.domain]) + link
        elif link.startswith(self.http) or link.startswith("http"):
            link = link
        else:
            link = "://".join([self.http, self.domain]) + "/" + link
        return link

    def is_alive(self):
        """Check if the drivr object is alive or not."""
        if self.__fresh__:
            return True
        try:
            self.driver.execute(Command.STATUS)
            return True
        except (socket.error, http.client.CannotSendRequest, MaxRetryError, TypeError, AttributeError):
            return False

    def check_robots(self, agent="*", **kwargs):
        """Checks robots on the domain."""
        agents = [agent]
        if agent != self.user_agent_string:
            agents.append(self.user_agent_string)
        self.save_to_log("Checking robots on domain %s" % self.domain)
        currurl = self.current_url
        self.__change_restrictions__ = True
        self.restrictions = []
        restrictions = []
        start_driver = False
        th = 2 if kwargs.get("th") is None else kwargs.get("th")
        if self.driver is None or not self.is_alive():
            start_driver = True
        self.get(self.complete_link("Robots.txt"), n=kwargs.get("n"), webdriver_log=kwargs.get("webdriver_log"),
                 timeout=kwargs.get("timeout"), th=th)
        bs1 = self.soup
        self.get(self.complete_link("robots.txt"), n=kwargs.get("n"), webdriver_log=kwargs.get("webdriver_log"),
                 timeout=kwargs.get("timeout"), th=th)
        bs2 = self.soup
        if start_driver:
            self.driver.quit()
        for _agent in agents:
            if "User-agent: %s" % _agent in bs1.get_text().replace("User-Agent", "User-agent"):
                cont = bs1.get_text().replace("User-Agent", "User-agent")
            elif "User-agent: %s" % _agent in bs2.get_text().replace("User-Agent", "User-agent"):
                cont = bs2.get_text().replace("User-Agent", "User-agent")
            else:
                self.restrictions = restrictions
                self.save_to_log("No restrictions found for agent %s. Robots assumed from parent Driver!" % _agent)
                if kwargs.get(".call") is None:
                    self.get(currurl)
                self.http, self.domain, self.path, self.params, self.query, self.fragment = urlparse(currurl)[:]
                self.current_url = currurl
                continue
            count2 = 0
            for __ in range(cont.count("User-agent: %s" % _agent) - 1):
                count1 = cont.index("User-agent: %s" % _agent, count2)
                count2 = cont.index("User-agent: ", count1 + 1)
                if "Disallow: " in cont[count1:count2]:
                    ccount2 = 0
                    for _ in range(cont[count1:count2].count("Disallow: ") - 1):
                        ccount1 = cont[count1:count2].index("Disallow: ", ccount2)
                        ccount2 = min(cont[count1:count2].index("\n", ccount1 + 1),
                                      cont[count1:count2].index("#", ccount1 + 1) if "#" in cont[
                                                                                            count1 + ccount1 + 1:count2]
                                      else 9999999999)
                        restrictions.append(cont[(count1 + ccount1 + 10):(count1 + ccount2)])
                    ccount1 = cont[count1:].index("Disallow: ", count1 + ccount2)
                    restrictions.append(cont[(count1 + ccount1 + 10):(count1 + ccount1 + 10 +
                                                                      min(cont[count1 + ccount1 + 10:].index("\n"),
                                                                          cont[count1 + ccount1 + 10:count2].index("#")
                                                                          if "#" in cont[count1 + ccount1 + 10:count2]
                                                                          else 9999999999))])
            count1 = cont.index("User-agent: %s" % _agent, count2)
            try:
                count2 = cont.index("User-agent: ", count1 + 1)
            except ValueError:
                count2 = len(cont)
            if "Disallow: " in cont[count1:count2]:
                ccount2 = 0
                for _ in range(cont[count1:count2].count("Disallow: ") - 1):
                    ccount1 = cont[count1:count2].index("Disallow: ", ccount2)
                    ccount2 = min(cont[count1:count2].index("\n", ccount1 + 1),
                                  cont[count1:count2].index("#", ccount1 + 1) if "#" in cont[
                                                                                        count1 + ccount1 + 1:count2]
                                  else 9999999999)
                    restrictions.append(cont[(count1 + ccount1 + 10):(count1 + ccount2)])
                ccount1 = cont[count1:].index("Disallow: ", ccount2)
                try:
                    restrictions.append(cont[(count1 + ccount1 + 10):(count1 + ccount1 + 10 +
                                                                      min(cont[count1 + ccount1 + 10:].index("\n"),
                                                                          cont[count1 + ccount1 + 10:count2].index("#")
                                                                          if "#" in cont[count1 + ccount1 + 10:count2]
                                                                          else 9999999999))])
                except ValueError:
                    restrictions.append(cont[(count1 + ccount1 + 10):])
        self.restrictions = restrictions
        self.save_to_log("Robots checked! Restrictions: %s" % self.restrictions)
        if kwargs.get(".call") is None:
            self.get(currurl)
        self.http, self.domain, self.path, self.params, self.query, self.fragment = urlparse(currurl)[:]
        self.current_url = currurl

    def robots_deny(self, link=None):
        """Returns list of websites that are denied by robots.txt file."""
        rep = ((":", "\\:"), ("?", "\\?"), ("-", "\\-"), ("+", "\\+"), ("$", "\\$"), (".", "\\."),
               ("\'", "\\\'"), ("[", "\\["), ("]", "\\]"), ("(", "\\("), (")", "\\)"), ("*", "\\*"))
        link = self.driver.current_url if link is None else link
        # Check middle of link (must include a "/" at the end of restriction)
        for restriction in self.restrictions:
            restriction_t = restriction
            for r, p in rep:
                restriction_t = restriction_t.replace(r, p).replace("\\*", ".*")
            if re.search("^" + restriction_t, "".join(urlparse(link)[2:])) is not None:
                return restriction
        return False

    def export_Driver(self):
        """Creates a clone of the Driver object with a non-active webdriver. Other attributes remain the same."""
        new = Driver(options=self.options, restrictions=self.restrictions, to_log=self.to_log,
                     proxy_port=self.proxy_port, profile=self.profile, executable_path=self.executable_path,
                     bins_path=self.bins_path)
        new.name = self.name
        new.n = self.n
        new.current_url = self.current_url
        new.http = self.http
        new.domain = self.domain
        new.meta = self.meta
        new.driver = None
        return new

    def add_to_meta(self, values, keywords=None):
        """Adds or updates the meta dictionary content with regards to the values and keywords given."""
        counters = [key[4:] for key in self.meta if isinstance(key, str) and key.startswith("meta")]
        for _ in counters:
            try:
                counters.append(int(counters.pop(0)))
            except TypeError:
                continue
        counter = max(counters) + 1
        if keywords is None:
            if isinstance(values, dict) or (isinstance(values, tuple) and len(values) == 2):
                self.meta.update(values)
            elif isinstance(values, list):
                self.meta.update(dict(["item" + str(c + counter), d] for c, d in enumerate(values)))
            else:
                self.meta.update({"item%d" % counter: values})
        elif isinstance(keywords, (list, tuple)) and len(keywords) == len(values):
            self.meta.update(dict([keywords[c], values[c]] for c in range(len(keywords))))
        else:
            raise IndexError("Number of keywords and values does not match")
