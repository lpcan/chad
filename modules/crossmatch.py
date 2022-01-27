#!/usr/bin/python
# Perform crossmatch with master table and another catalogue, using XMatch
# L. Canepa, adapted from V.A. Moss
__author__ = "L. Canepa"
__version__ = "0.2"

import numpy as np
from astropy import units as u
from astroquery.xmatch import XMatch
from astroquery.utils.tap.core import TapPlus
from astropy.io import ascii
from scipy.stats import circmean
import time
import glob
import os

def crossmatch(master, max_confidence, force):
	
	# Get the surveys to crossmatch
	surveys = ascii.read("input/chadsurveys.csv", format = "csv")
	
	for survey in surveys:
		if survey["status"] == "blocked":
			continue

		# Get the master files
		masterfiles = glob.glob("input/%s_%s*csv" % (master, survey["type"]))

		# Get already processed files
		if not os.path.exists("output"):
			os.makedirs("output")
		processed = glob.glob("output/*")

		for file in masterfiles:
			chunk = file.split('_')[-1].split('.')[0]
			name = survey["survey"]
			v_code = survey["vizier_code"]
			ang_sep = survey["angular_sep"]

			# Check if table is available
			available = XMatch.is_table_available("vizier:%s" % v_code)
			if not available:
				print("Table %s is not available! Continuing..." % v_code)
				break

			# Check if this survey has already been matched
			done = False
			for p in processed:
				if "%s_%s_%s_%s.csv" % (master, survey['type'], name.lower().replace(" ", "_"), chunk) in p and not force:
					print("Table %s_%s has already been processed! Continuing..." % (name.lower().replace(" ", "_"), chunk))
					done = True
					break
			if done == True:
				break
					
			start = time.time() # Time the crossmatch
			print("Crossmatching %s with file %s" % (name, file))
			try:
				matches = XMatch.query(cat1 = open(file), cat2 = "vizier:%s" % v_code, max_distance = ang_sep * u.arcsec, colRA1 = "ra", colDec1 = "dec")
			except Exception as inst:
				print("Query failed: %s. Continuing..." % inst)
				continue

			print("Culling crossmatch results... Max confidence level: %s%%" % str(max_confidence))
			
			# Calculate the confidence of each match and remove matches < confidence level
			confidence = calc_confidence(v_code, matches, file, max_sep = ang_sep)
			matches['confidence'] = confidence
			matches = matches[matches['confidence'] > (max_confidence/100)]

			# Prepare table for saving
			table = ascii.read(file, format="csv")
			# Only want to save angDist, master id, and target table columns
			matches = matches[matches.colnames[:2] + matches.colnames[len(table.colnames) + 1:]]

			# Save the crossmatched result to use later
			print("Writing table...")
			ascii.write(matches, "output/%s_%s_%s_%s.csv" % (master, survey['type'], name.lower().replace(" ", "_"), chunk), overwrite=True)
			end = time.time()
			total = end-start
			print("Total time: %.2f min" % (total/60.))
			
	print("Done crossmatching!")

def calc_confidence(target_name, matches, master, max_sep):

	table = ascii.read(master, format = "csv")

	# Estimate the density of the target survey by getting number of elements in a 1 degree radius around a random point in the patch -- TODO: how to get the "centre" of a patch that is weird and elongated e.g. racs galactic region
	rand_ra = matches['ra'][int(len(matches) / 2)]
	rand_dec = matches['dec'][int(len(matches) / 2)]

	# Count the number of sources in a 1 degree radius circle for both catalogues
	data = TapPlus(url="http://tapvizier.u-strasbg.fr/TAPVizieR/tap")
	job = data.launch_job_async(f"SELECT COUNT(*) FROM \"{target_name}\" WHERE 1=CONTAINS(POINT('ICRS', RAJ2000, DEJ2000), CIRCLE('ICRS', {rand_ra}, {rand_dec}, 1))")
	r = job.get_results()

	density = r[0][0] / np.pi
	density = density / (60*60*60*60) # Convert density to arcseconds^2 instead of deg^2

	# Calculate the confidence for each point in the table
	confidence = []
	for i, source in enumerate(matches):
		print(f"{i}/{len(matches)}", end='\r')

		if source["angDist"] > max_sep - 0.2:
			confidence.append(-1)
			continue

		r = source["angDist"]
		upper = r + 0.2
		lower = r - 0.2

		if lower < 0:
			lower = 0
			upper = 0.4

		area = np.pi * upper**2 - np.pi * lower**2
		all_matches = matches[matches["angDist"] >= lower]
		all_matches = len(all_matches[all_matches["angDist"] <= upper])

		# Confidence = 1 - (expected number of matches with random uniform distribution / actual number of matches)
		prob = density * area * len(table) / all_matches
		prob = 1 - prob
		confidence.append(round(prob, 4))
	print(f"{i+1}/{len(matches)}\n", end = '')
	
	return confidence
		


