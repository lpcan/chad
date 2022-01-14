import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import numpy as np

def connect():
    conn = psycopg2.connect("dbname=chad user=postgres password=hello")
    cur = conn.cursor()
    return conn, cur

# Perform a positional search against RACS catalogues
def cone_search(ra, dec, radius, cat):
    conn, cur = connect()
    # Convert everything to radians
    radius = np.radians(radius / 60)
    ra = np.radians(ra)
    dec = np.radians(dec)

    # Perform cone search through database
    cur.execute("SELECT * FROM " + cat + " WHERE ACOS(SIN(RADIANS(dec))*SIN(%s)+COS(RADIANS(dec))*COS(%s)*\
                COS(RADIANS(ra)-%s)) < %s ORDER BY SQRT(POWER(RADIANS(ra)-%s,2)+POWER(RADIANS(dec)-%s,2))",\
                (dec, dec, ra, radius, ra, dec))
    results = cur.fetchmany(50) # Return first 50 results?
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

    return result