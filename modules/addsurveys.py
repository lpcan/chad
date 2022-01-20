#!/usr/bin/python
# Import crossmatches into CHAD
# L. Canepa
__author__ = "L. Canepa"
__version__ = "0.2"

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
from astropy.io import ascii
import os
from . import functions as f
import glob
import numpy as np

passwd = "hello"

def addsurveys():

    # Get the surveys to be added
    surveys = ascii.read("input/chadsurveys.csv", format = "csv")

    # Connect to CHAD if it exists
    try:
        conn = psycopg2.connect("host=localhost dbname=chad user=postgres password=%s" % passwd)
    except:
        print("ERROR: Could not connect to CHAD. Try running rebuild")
    cur = conn.cursor()

    # Process one survey at a time
    for survey in surveys:
        name = survey["survey"]
        table_name = name.lower()

        if survey["status"] != "import":
            print("Table %s not marked as import, continuing..." % name)
            continue

        # Delete the old table if it exists
        cur.execute('DROP TABLE IF EXISTS %s;' % table_name)
        conn.commit()
        
        # Go through all crossmatch result files for this survey
        csvs = glob.glob("output/*%s*" % table_name)

        for i, file in enumerate(csvs):
            # Read in the table
            print("Reading in Table %s (%s)..." % (name, file))
            table = ascii.read(file)
            #print(table.keys())

            # Generate the header for the first file
            if i == 0:
                prim_key = None
                # Select primary key
                for key in table.keys():
                    if key != "id" and "id" in key.lower() and key != "confidence": # Select an id column, but not the RACS id column
                        prim_key = key
                # Could not find a primary key, try to find a different key
                if prim_key == None:
                    # Try to find an alternate prim_key
                    for key in table.keys():
                        if table_name in key.lower():
                            prim_key = key # Set primary key as source name (usually in a column called table_name)
                # If prim_key is still none, ask for user to set primary key
                if prim_key == None:
                    while prim_key not in table.keys():
                        if prim_key != None: print("Invalid column name, please try again.")
                        prim_key = input("Please enter a column name for primary key: ")

                header = f.generate_header(table, table_name, prim_key=prim_key)
                print(header)
                # Create the table
                cur.execute(header)
            
            print("Inserting rows...")
            for j, source in enumerate(table):
                print(f"{j}/{len(table)}", end = '\r')

                # If same source appears multiple times (matched to multiple RACS sources), take the closest
                matches = table[table[prim_key] == source[prim_key]]

                if len(matches) > 1:
                    # If this isn't the closest match, skip
                    if source['angDist'] != min(matches['angDist']):
                        continue
                
                values = ", ".join(['%s'] * len(source))
                query = "INSERT INTO %s VALUES (" % table_name
                ssource = list(map(str, source))

                # Check for invalid values
                for c in range(len(ssource)):
                    if ssource[c] == "--":
                        ssource[c] = None

                cur.execute(query + values + ")", ssource)
                
            print(f"{j+1}/{len(table)}")

    # Commit the changes back to the database
    print("Done!")
    conn.commit()
    

            
