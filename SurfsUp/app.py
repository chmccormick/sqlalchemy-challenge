# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

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
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to My Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #Create session (link) from Python to the DB
    session = Session(engine)

    """Return json representatjion of precipitation analysis """
    # Query for precipitation scores over the last 12 months
    last_twelve_months = dt.date(2017, 8, 23) - dt.timedelta(days=356)
    last_date = dt.date(last_twelve_months.year, last_twelve_months.month, last_twelve_months.day)

    prcp_results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_date).order_by(Measurement.date)

    session.close()

    # Convert query results to dictionary
    prcp_dict = dict(prcp_results)

    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return json list of stations from dataset"""
    # Query for all station info for each station
    sel = [Station.station, Station.name, Station.latitude, Station.longitude]
    station_results = session.query(*sel).all()
    session.close()

    # Create a dictionary from station data and append to station list 
    stations_list = []

    for station, name, latitude, longitude in station_results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        stations_list.append(station_dict)

    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return dates and temp observations of the most-active station"""
    # Query for lst 12 months of temp observation for most-active station
    tobs_resuls = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= '2016-08-23').all()
    session.close()

    # Create a dictionary from query results and append it to tobs list
    tobs_list =[]
    for date, tobs in tobs_resuls:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def get_start_temps(start):
    # Create session (link) from Python to the DB
    session = Session(engine)
    
    """Return json list of min, avg, and max temps for a specified start date"""
    # Query for min, avg, and max temps for a given start date
    start_results = session.query(func.min(Measurement.tobs),
                                  func.avg(Measurement.tobs),
                                  func.max(Measurement.tobs)).\
                                  filter(Measurement.date >= start).all()
    session.close()

    # Create a dictionary from the query results and append it to the start list
    start_list = []
    for min_temp, avg_temp, max_temp in start_results:
        start_dict = {}
        start_dict["minimum temperature"] = min_temp
        start_dict["average temperature"] = avg_temp
        start_dict["max temperature"] = max_temp
        start_list.append(start_dict)

    return jsonify(start_list)


@app.route("/api/v1.0/<start>/<end>")
def get_start_end_temps(start,end):
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return json list of min, avg, and max temps for dates from specified start to end"""
    # Query foor min, avg, and max temps for a given start date
    start_end_results = session.query(func.min(Measurement.tobs),
                                  func.avg(Measurement.tobs),
                                  func.max(Measurement.tobs)).\
                                  filter(Measurement.date >= start).\
                                  filter(Measurement.date <= end)
    
    session.close()

    # Create a dictionary from the query results and append it to the start_end list 
    start_end = []
    for min_temp, avg_temp, max_temp in start_end_results:
        start_end_dict = {}
        start_end_dict["minimum temperature"] = min_temp
        start_end_dict["average temperature"] = avg_temp
        start_end_dict["max temperature"] = max_temp
        start_end.append(start_end_dict)

        return jsonify(start_end)
    


if __name__ == '__main__':
    app.run(debug=True)