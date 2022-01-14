import numpy as np
from flask import Flask, render_template, request, redirect, url_for
import db

app = Flask(__name__)

@app.route('/')
def home(search_error = False):
    return render_template("home.html", search_error = search_error)

@app.route('/result', methods=["POST", "GET"])
def results():
    if request.method == "GET":
        return redirect(url_for("home"))

    # Check the coordinates format
    ra = request.form['ra']
    dec = request.form['dec']
    radius = request.form['radius']
    cattype = request.form['cattype']
    table = "racs_"+cattype
    try:
        ra = float(ra)
        dec = float(dec)
        radius = float(radius)
    except:
        return render_template("home.html", search_error = True) # Invalid request

    # Get the results from the database
    results = db.cone_search(ra, dec, radius, table)
    colnames = db.colnames(table)
    # Find the columns we want
    name_idx = results[0].index([x for x in results[0] if type(x) == str][0])
    name = [x[name_idx] for x in results] # Take first column with type string as source name
    ra_idx = colnames.index([x for x in colnames if "ra" in x][0])
    source_ra = [x[ra_idx] for x in results]
    dec_idx = colnames.index([x for x in colnames if "dec" in x][0])
    source_dec = [x[dec_idx] for x in results]
    ids = [x[0] for x in results]

    return render_template("results.html", search_params=(ra, dec, radius, table), results=(name, source_ra, source_dec), ids=ids)

@app.route('/<table>/<int:id>')
def show(id, table):
    # Get the master table information about the source
    source = db.search_id(id, table)
    colnames = db.colnames(table)
    
    return render_template("show.html", source=source, colnames=colnames)