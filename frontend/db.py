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

# Get a list of all tables in the database
def get_tables():
    conn, cur = connect()

    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema')")
    tables = cur.fetchall()
    tables = [table[0] for table in tables if table[0] != "match_info"]

    cur.close()
    conn.close()

    return tables

# Return a list of column names from the database
def colnames(cat):
    conn, cur = connect()

    cur.execute("SELECT * FROM " + cat + " LIMIT 0")
    colnames = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    return colnames

# Perform a positional search against RACS catalogues. 
# Constraints must be passed in as a list of tuples where each constraint = (colname, min=None, max=None)
def cone_search(ra, dec, radius, cat, min_flux = None, force_match = None):
    conn, cur = connect()
    # Convert everything to radians
    radius = np.radians(radius / 60)
    ra = np.radians(ra)
    dec = np.radians(dec)

    flux_constraint = ""
    values = (dec, dec, ra, radius, dec, dec, ra)
    if min_flux != None:
        flux_constraint = " AND peak_flux >= %s"
        values = (dec, dec, ra, radius, min_flux, dec, dec, ra)

    # Perform cone search with conditions (if any)
    if force_match != None: 
        # Only select rows that have a match in the other table
        cur.execute(sql.SQL("SELECT {}.* FROM {} INNER JOIN {} ON {}.id = {}.id WHERE \
                    ACOS(SIN(RADIANS(dec))*SIN(%s)+COS(RADIANS(dec))*COS(%s)*\
                    COS(RADIANS(ra)-%s)) < %s" + flux_constraint + " ORDER BY ACOS(SIN(RADIANS(dec))*SIN(%s)+\
                    COS(RADIANS(dec))*COS(%s)*COS(RADIANS(ra)-%s))").format(sql.Identifier(cat), sql.Identifier(cat), \
                    sql.Identifier(force_match), sql.Identifier(cat), sql.Identifier(force_match)), values)
    else:
        cur.execute(sql.SQL("SELECT * FROM {} WHERE ACOS(SIN(RADIANS(dec))*SIN(%s)+COS(RADIANS(dec))*COS(%s)*\
                    COS(RADIANS(ra)-%s)) < %s" + flux_constraint + " ORDER BY ACOS(SIN(RADIANS(dec))*SIN(%s)+\
                    COS(RADIANS(dec))*COS(%s)*COS(RADIANS(ra)-%s))").format(sql.Identifier(cat)), values)

    results = cur.fetchmany(100) # Return first 100 results?
    cur.close()
    conn.close()

    return results

# Search for the closest source to a given RA and DEC
def search_closest(ra, dec, table, min_flux = None, force_match = None):
    conn, cur = connect()

    flux_constraint = ""
    values = (ra, dec, dec)
    if min_flux != None:
        flux_constraint = " WHERE peak_flux >= %s"
        values = (min_flux, ra, dec, dec)

    if force_match != None:
        # Using the small angle approximation since we assume there will always be a source < 1 degree away
        cur.execute(sql.SQL("SELECT {}.* FROM {} INNER JOIN {} ON {}.id = {}.id" + flux_constraint +" ORDER BY \
                    SQRT(POWER((%s-ra)*COS(%s), 2)+POWER(%s-dec, 2)) ASC LIMIT 1").format(sql.Identifier(table),\
                    sql.Identifier(table), sql.Identifier(force_match), sql.Identifier(table), sql.Identifier(force_match)), \
                    values)
    else:
        cur.execute(sql.SQL("SELECT * FROM {}" + flux_constraint + " ORDER BY SQRT(POWER((%s-ra)*COS(%s), 2)+\
                    POWER(%s-dec, 2)) ASC LIMIT 1").format(sql.Identifier(table)), values)

    result = cur.fetchone()

    conn.close()
    cur.close()

    return result

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

    # Get a list of all other possible matching tables
    if "racs" in curtable:
        cur.execute("SELECT match_table FROM match_info WHERE racs_table = %s", (curtable,))
        tables = cur.fetchall()
        tables = [table[0] for table in tables]
    else:
        cur.execute("SELECT racs_table FROM match_info WHERE match_table = %s", (curtable,))
        racs_table = cur.fetchone()[0]
        cur.execute("SELECT match_table FROM match_info WHERE racs_table = %s", (racs_table,))
        tables = cur.fetchall()
        tables = [racs_table] + [table[0] for table in tables if curtable not in table[0]]
    
    # Search through all other tables for matching object
    match_tables = []
    for table in tables:
        cur.execute("SELECT * FROM " + table + " WHERE id = %s", (id,))
        m = cur.fetchall()
        if len(m) > 0:
            match_tables.append(table)

    cur.close()
    conn.close()
    return match_tables

# For a given source, find all associated components
def find_components(source_id):
    conn, cur = connect()

    # Get all components associated with this source
    cur.execute("SELECT id, gaussian_id, ra, dec FROM racs_component WHERE source_id = %s", (source_id,))
    comp = cur.fetchall()

    cur.close()
    conn.close()

    return comp

# Search for an exact value in a given table column
def search_exact(table, colname, constraint):
    conn, cur = connect()

    # Perform the search
    cur.execute(sql.SQL("SELECT id FROM {} WHERE {} = %s").format(sql.Identifier(table), sql.Identifier(colname)), (constraint,))
    r = cur.fetchmany(50)
    
    cur.close()
    conn.close()

    return r

# Get the matching RACS table
def get_racs_table(curtable):
    conn, cur = connect()

    cur.execute("SELECT racs_table FROM match_info WHERE match_table = %s", (curtable,))
    racs_table = cur.fetchone()[0]

    cur.close()
    conn.close()

    return racs_table