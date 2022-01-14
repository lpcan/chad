#!/usr/bin/python
# Helper functions
# L. Canepa, adapted from V.A. Moss

import sys
import requests

# Download information from Google spreadsheet
def download_csv(sheet_id):

	url = "https://docs.google.com/spreadsheets/d/%s/export?exportFormat=csv" % sheet_id
	res = requests.get(url=url)
	open("input/chadsurveys.csv", "wb").write(res.content)
	
	return
	
# Generate SQL table header from csv file
def generate_header(table, table_name, prim_key = "id"):

	# Check that primary key exists
	if prim_key not in table.keys():
		print("ERROR: Please specify an existing column name for primary key")
		sys.exit()

	# Determine key type
	keytypes = []
	dbkeys = table.keys()
	for k in range(0, len(dbkeys)):
		key = dbkeys[k]
		keytype = str(table[key].dtype)
		
		# Determine type for database
		if "int" in keytype:
			keytypes.append("BIGINT")
		elif "float" in keytype:
			keytypes.append("FLOAT")
		elif "<U" or "str" in keytype:
			keytypes.append("TEXT")
		else:
			print("Type uncertain: %s... exiting!" % keytype)
			sys.exit()

		# Deal with bad column names
		if key[0].isdigit() == True:
			dbkeys[k] = 'x'+key
		if '.' in key:
			dbkeys[k] = '\"'+key+'\"'
		if key != "id" and key.lower() == "id": # check that foreign key "id" (from master) is not duplicated here
			# Duplicate column
			dbkeys[k] = key+"_x"

			
	# Generate create table command
	header = "CREATE TABLE %s(\n" % table_name
	
	for i in range(0, len(dbkeys)):
		if dbkeys[i] == prim_key or dbkeys[i] == prim_key+"_x":
			header = header + "%s %s PRIMARY KEY,\n" % (dbkeys[i], keytypes[i])
		else:
			header = header + "%s %s,\n" % (dbkeys[i], keytypes[i])
	header = header[:-2]+"\n)"
	
	return header
