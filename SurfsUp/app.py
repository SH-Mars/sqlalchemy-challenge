 # Import the dependencies.
import numpy as np
from pathlib import Path
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
database_path = Path('../Resources/hawaii.sqlite')
engine = create_engine(f"sqlite:///{database_path}")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# home page, list all routes
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Avaliable Routes:<br/>"
        "<a href='http://127.0.0.1:5000/api/v1.0/precipitation'>Precipitation</a><br/>"
        "<a href='http://127.0.0.1:5000/api/v1.0/stations'>Stations</a><br/>"
        "<a href='http://127.0.0.1:5000/api/v1.0/tobs'>Temperatures</a><br/>"
        f"http://127.0.0.1:5000/api/v1.0/[start] replace start with the start date, for example 2012-01-01 <br/>"
        f"http://127.0.0.1:5000/api/v1.0/[start]/[end] replace start & end with the start date & end date, for example 2012-01-01/2016-01-01"
    )

# precipitation route
# return a json with date and prcp
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').\
            filter(Measurement.date <= '2017-08-23').order_by(Measurement.date).all()
    session.close()
    df = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        df.append(precipitation_dict)
    return jsonify(df)

# stations route
# return all the station in measurement table
@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    results = session.query(func.distinct(Measurement.station)).all()
    session.close()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

# tobs route
# return date and tob of the most active station for last year only
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= '2016-08-23').\
            filter(Measurement.date <= '2017-08-23').all()
    session.close()
    df = []
    for date, tob in results:
        tobs_last_year = {}
        tobs_last_year[date] = tob
        df.append(tobs_last_year)
    return jsonify(df)

# <start> route
# for user to specify the start date and return the min, max, avg of observed temperature from the start date till the end date in the table
@app.route("/api/v1.0/<start>")
def start(start):
    """Fetch the min, max, avg of observed temperatures from the start variable supplied by the user, or a 404 if not."""
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
    df = []
    for min, max, avg in results:
        define_start = {}
        define_start['TMIN'] = min
        define_start['TAVG'] = avg
        define_start['TMAX'] = max
        df.append(define_start)
    return jsonify(df)

# <start/end> route
# for user to specify the start and end date, and return the min, max, avg of observed temperature from the start date to end date 
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Fetch the min, max, avg of observed temperatures from the start and end variables supplied by the user, or a 404 if not."""
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    df = []
    for min, max, avg in results:
        define_start_end = {}
        define_start_end['TMIN'] = min
        define_start_end['TAVG'] = avg
        define_start_end['TMAX'] = max
        df.append(define_start_end)
    return jsonify(df)

if __name__ == "__main__":
    app.run(debug=True)