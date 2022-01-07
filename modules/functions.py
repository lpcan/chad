#!/usr/bin/python
# Helper functions
# L. Canepa, adapted from V.A. Moss

import requests
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from termcolor import colored

# Download information from Google spreadsheet
def download_csv(sheet_id):

	url = "https://docs.google.com/spreadsheets/d/%s/export?exportFormat=csv" % sheet_id
	res = requests.get(url=url)
	open("input/chadsurveys_readonly.csv", "wb").write(res.content)
	
	return
	
# Delete database and create again
def rebuild():
	
	print("Connecting to host...")
	passwd = input("Password for user postgres: ")
	conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=%s" % passwd)
	conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
	cur = conn.cursor()
	cur.execute("DROP DATABASE IF EXISTS chad;")
	conn.commit()
	cur.execute("CREATE DATABASE chad;")
	print(colored("Done rebuild", "green"))
	
	return
