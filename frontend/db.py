# Database functions
# L. Canepa

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import numpy as np

# Open a connection to the database
def connect():
    conn = psycopg2.connect("dbname=chad user=postgres password=hello")
    cur = conn.cursor()
    return conn, cur

# Perform a positional search against RACS catalogues. 
# Constraints must be passed in as a list of tuples where each constraint = (colname, min=None, max=None)
def cone_search(ra, dec, radius, cat, min_flux = None):
    conn, cur = connect()
    # Convert everything to radians
    radius = np.radians(radius / 60)
    ra = np.radians(ra)
    dec = np.radians(dec)

    flux_condition = ""
    if min_flux != None: 
        # Construct flux constraint
        # Perform cone search with conditions (if any)
        cur.execute(sql.SQL("SELECT * FROM {} WHERE ACOS(SIN(RADIANS(dec))*SIN(%s)+COS(RADIANS(dec))*COS(%s)*\
                    COS(RADIANS(ra)-%s)) < %s AND peak_flux >= %s ORDER BY SQRT(POWER(RADIANS(ra)-%s,2)+\
                    POWER(RADIANS(dec)-%s,2))").format(sql.Identifier(cat)), (dec, dec, ra, radius, min_flux, ra, dec))
    else:
        cur.execute(sql.SQL("SELECT * FROM {} WHERE ACOS(SIN(RADIANS(dec))*SIN(%s)+COS(RADIANS(dec))*COS(%s)*\
                    COS(RADIANS(ra)-%s)) < %s ORDER BY SQRT(POWER(RADIANS(ra)-%s,2)+\
                    POWER(RADIANS(dec)-%s,2))").format(sql.Identifier(cat)), (dec, dec, ra, radius, ra, dec))

    results = cur.fetchmany(100) # Return first 100 results?
    cur.close()
    conn.close()

    return results

# Return a list of column names from the database
def colnames(cat):
    conn, cur = connect()

    cur.execute("SELECT * FROM " + cat + " LIMIT 0")
    colnames = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    return colnames

# Search for a source by id
def search_id(id, table):
    conn, cur = connect()

    cur.execute("SELECT * FROM " + table + " WHERE id = %s", (id,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result

# Return other tables with an id match
def get_matches(id, curtable):
    conn, cur = connect()

    # Get a list of all other tables
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema')")
    tables = cur.fetchall()

    tables = [table for table in tables if curtable not in table[0]]

    # Reorder the tables to have RACS at the start
    for i, table in enumerate(tables):
        if "racs" in table:
            temp = tables[0]
            tables[0] = tables[i]
            tables[i] = temp
    
    # Search through all other tables for matching object
    match_tables = []
    for table in tables:
        cur.execute("SELECT * FROM " + table[0] + " WHERE id = %s", (id,))
        m = cur.fetchall()
        if len(m) > 0:
            match_tables.append(table[0])

    cur.close()
    conn.close()
    
    return match_tables
    
def find_components(source_id):
    conn, cur = connect()

    # Get all components associated with this source
    cur.execute("SELECT id, gaussian_id, ra, dec FROM racs_component WHERE source_id = %s", (source_id,))
    comp = cur.fetchall()

    cur.close()
    conn.close()

    return comp

def search_exact(table, colname, constraint):
    conn, cur = connect()

    # Perform the search
    cur.execute(sql.SQL("SELECT id FROM {} WHERE {} = %s").format(sql.Identifier(table), sql.Identifier(colname)), (constraint,))
    r = cur.fetchmany(50)
    
    cur.close()
    conn.close()

    return r