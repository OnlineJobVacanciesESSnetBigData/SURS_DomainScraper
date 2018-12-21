# scraping_JobPortals
Programs and documentation regarding scraping of Job Portals. This project runs in Python 3.4 or more. It is **not** supported in Python 2.7. It also uses a *selenium* simulation browser. Without it, the project will not run correctly. 

In our case this is a Mozilla Firefox browser which additionally needs a geckodriver executable. **It is recommended that you use a browser of version 61.0.2 (Firefox Quantum) and a geckodriver version 0.20.1**

###### *Keep in mind that all internet domains, paths to directories and files, file names and HTML tags are examples and should be changed before use.*

### List of all imported modules in Python:

(basic operations on files, foldiers and system-specific parameters)
* os,
* sys,
* windll,

(file reading)
* csv,

(date and time formatting)
* time,
* datetime,

(internet connections)
* selenium,
* urllib.request,

(HTML reading and parsing)
* bs4,
* re, 

(multithreading)
* multiprocessing,

(asynchronous events handling)
* signal
