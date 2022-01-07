#!/usr/bin/python
# Helper functions
# L. Canepa, adapted from V.A. Moss

import requests

# Download information from Google spreadsheet
def download_csv(sheet_id):

	url = "https://docs.google.com/spreadsheets/d/%s/export?exportFormat=csv" % sheet_id
	res = requests.get(url=url)
	open("input/chadsurveys.csv", "wb").write(res.content)
	
	return
	
# Generate SQL table header from csv file
def generate_header(file, table_name):
	# Determine key type
	keytypes = []
	dbkeys = d.keys()
	for k in range(0, len(dbkeys)):
		key = dbkeys[k]
		keytype = str(d[key].dtype)
		print(key, keytype)
		
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
			
	# Generate create table command
	header = "CREATE TABLE %s(\nid TEXT PRIMARY KEY,\ntype TEXT,\n" % table_name
	
	for i in range(0, len(dbkeys)):
		header = header + "%s %s,\n" % (dbkeys[i], keytypes[i])
	header = header[:-2]+"\n)"
	
	return header
