#!/bin/bash
#
# synch data to amazon s3
#

# make sure using python 2.7
PATH=/usr/local/bin:$PATH
export PATH

PYTHONPATH=/usr/lib/python2.7/site-packages
export PYTHONPATH

# set lang to UTF8
LANG=en_US.UTF-8
export LANG

kasastore -s file:///Storage/Documents \
          -d s3:///docs.kasa.sample.domain/Documents >> ./kasa.log 2>&1
