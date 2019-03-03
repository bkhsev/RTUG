# RTUG
RTUG is an application that plots graphs of russian stock prices in USD (United States Dollar) to compensate for the long-run devaluation of the RUB (Russian Ruble).

## Prerequisites
RTUG uses Python 2.7 and the following python modules:

#### Third-party modules
- dash
- plotly
- stockstats
- pandas 
- numpy
- datetime

#### Modules embedded in Python
(This modules do not require installation)
- urllib2 
- csv
- re


## Installation

1. Fork and clone the RTUG [repo](https://github.com/bkhsev/RTUG).

**Either**

In terminal,

`$ git clone https://github.com/bkhsev/RTUG.git`
 
 **Or**
 
 ![Alt Text](https://github.com/bkhsev/files-used-in-other-repos/blob/master/clone.gif)
 
 
 2. To set up your development/testing environment, run the following commands:
 
 ``` bash
# Move into the clone
$ cd dash
# Create a virtualenv
$ python2 -m venv venv
# Activate the virtualenv
$ . venv/bin/activate
# (On Windows, the above would be: venv\scripts\activate)
# Install required dependencies
$ pip install -r additional/requirements.txt
 ```
 
 You are set and ready to begin! :rocket:
