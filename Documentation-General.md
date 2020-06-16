# Documentation for Slovenian scraping of internet pages
## In general
This document overviews 
Scraping is done with Python programmes using the Selenium module for itnernet browser simulation. This is done in order to use the 
browser's functionalities when running scripts. Our chosen browser is a Mozilla Firefox browser which also needs a geckodriver 
executable to work with Selenium. 

The browser works in headless mode, which means it works in the background and does not disrupt other work. Simulating human browsing 
also decreases the possibility to be recognized as a computer and thus be denied access to pages. However, we still adhere to the 
*netiquette* and use it rationally and in a considerate manner to both the internet site owners as well as other users.

The downside to the simulation method is a rather slow manner, as loading of a page needs to be executed before scraping.

The scraping is done through a three-tier application process:
 * the object _Driver_ (from the _custom_driver_ module) handles a browser simulation, connection to and interaction with a page; it also
 automatically executes the Robots.txt restriction check everytime the domain name is changed,
 * a domain-specific application (a general example is represented in the _domain_tags.py_ file) must be written, which instructs the
 _Driver_ object what to do and what to return from the page once connected,
 * the object _Scraper_ (from the _custom_scraper_ module) manages multiple multithread processes of _Driver_ objects and collects the 
 _domain_tag_ responses.
 
Additional general functionalities are included in the _scraping_aux_ model, like dynamic button pressing, previous links comparison 
etc., and can be updated with new custom functions.

**Warning:** as said above, the _Driver_ objects need two executables to work correctly. After cloning this repository, an update to 
the code of the object must be made with the correct paths of both executables and to a desired map where log files will be saved.

**Warning:** we would advise you to add the path of the repository to the computer's environmental variables, so that your local Python 
interpreter can easily load them. If not, you will need to always specify the path to the repository before using it.

## SURS' general scraping robot
The _Scraper_ takes the name of the project (and the resulting files, be they to be saved), the target internet domain or a list of
target pages and other keyword arguments (are described in detail in the relevant document) as input. Before starting the scraping 
process, the robot will check the (first) target page's robots.txt and Robots.txt page for scraping restrictions. Users can also specify 
Firefox profiles to run the _Scraper_ with and it will in turn use the same profile on the _Driver_ objects.

Then the specified number (default: 3) of _Driver_ object robots will initialize on the target pages and collect the information 
according to the _domain_tag_ instructions. If the number of target pages is higher than the number of _Driver_ objects, each object 
will automatically continue its job on the next page after waiting for a appropriate amount of time (default: 3 seconds). While working 
the robots will also log their work to a specified logfile or else to the output window.

The ouputs of each _Driver_ object are 3 lists, which are collected by the _Scraper_ object. The first is automatically saved to a 
.csv file if specified so. The each _Driver_'s log is also collected into a common logfile with records ordered by their timestamp.

The robot has some automatic error handling as well. After an unsucessful connection to a page, the robot automatically retries to 
connect. The default behaviour is to retry for 2 more times before giving up. Additionally a timeout interval can be specified, which
specifies the time every _Driver_ object allows to pass before returning a Timeout error. This timeout interval has a value of 20 seconds
if no other value is inputted.


