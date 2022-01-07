#!/usr/bin/python
# Perform crossmatch with RACS and another catalogue, using XMatch
# L. Canepa, adapted from V.A. Moss
__author__ = "L. Canepa"
__version__ = "0.2"

from astropy import units as u
from astroquery.xmatch import XMatch
from astropy.io import ascii
import time
from modules import functions as f
import glob

def crossmatch():
	
	# Get the surveys to crossmatch
	surveys = ascii.read("input/chadsurveys.csv")
	
	for survey in surveys:
		
		masterfiles = glob.glob("input/racs*%s.csv" % survey["type"])
		
		
