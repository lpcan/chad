#!/usr/bin/python
# Module to delete and rebuild CHAD database with just master catalogue.
# L. Canepa, adapted from V.A. Moss
__author__ = "L. Canepa"
__version__ = "0.2"

import glob
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from astropy.io import ascii
from . import functions as f

def rebuild():
	
	# Connect to the host to rebuild database
	passwd = input("Password for user postgres: ")
	conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=%s" % passwd)
	conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
	cur = conn.cursor()
	cur.execute("DROP DATABASE IF EXISTS chad;")
	conn.commit()
	cur.execute("CREATE DATABASE chad;")
	
	# Add the base catalogue to CHAD
	print("Adding base catalogue to CHAD...")
	add_master(cur, "racs")

	
	
	print("Done rebuild")
	
	return
	
# Add the master catalogue (RACS) to the database
def add_master(cursor, name = "racs"):
	
	# Get both catalogue types into the database
	for cattype in ["component", "island"]:
	
		cats = glob.glob("input/%s_%s*.csv" % (name, cattype))
		
		# Loop over the input tables
		for i, cat in enumerate(cats):
			print("Reading in Table %s..." % cat)
			d = ascii.read(cat)
			
			# Generate the header
			if i == 0:
				header = f.generate_header(d, name+"_"+cattype)
				#print(header)
				
			# Create the table
			cursor.execute(header)

			# Insert rows into the table
			print("Inserting rows...")
	
	return
