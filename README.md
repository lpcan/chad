# chad

### Building CHAD
The backend of CHAD is built on postgres. When running `build_chad.py`, there are optional arguments for rebuilding, crossmatching, and adding surveys to the database. Before running these, the `passwd` variable at the top of `rebuild.py` and `addsurveys.py` needs to be changed to your postgres password (is there a way of building the database that doesn't require a password?). 

`rebuild.py` drops and adds the database, and adds the base racs catalogues to the database. The racs catalogues should be in the folder input/, named after their catalogue type, so that they can be accessed by `racs_component*.csv` or `racs_island*.csv`. `crossmatch.py` reads from a google sheet of input surveys, located at "https://docs.google.com/spreadsheets/d/1-ePYYFph6GHohn5KKZi24rw_vAdcMltg0lRu8FfSaPg/edit#gid=0", performs the crossmatch, culls matches based on match confidence level (calculated based on the density of the matching catalogue and the number of random matches expected at different radii) and stores the result in the output/ folder. If the survey has already been crossmatched, it will be skipped by default. CHAD can be forced to reperform the crossmatch by specifying the argument -f when running `build_chad.py`. Finally, `addsurveys.py` goes through the crossmatch results stored in output/ and adds them as new tables into the database. 

### CHAD Frontend
The frontend of CHAD runs using Flask. The postgres password will need to be changed in the `connect()` function in `frontend/db.py`. 

To run the flask app on a Mac, first run `export FLASK_APP=chad FLASK_ENV="development"` to set the main app file and specify a development environment (to avoid warnings). Then the server can be started with `flask run`, and CHAD can be accessed at localhost:5000.
