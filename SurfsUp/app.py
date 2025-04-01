# Import the dependencies
from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Flask Setup
#################################################

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True)

#################################################
# Database Setup
#################################################

# create a reference to the dataset

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Routes
#################################################

@app.route("/")
def Homepage():
    return (
        f"<center><h2>Welcome to the Climate Analysis API!</h2></center><br/>"
        f"<center><h3>Available Routes:</h3></center><br/>"
        f"<center>/api/v1.0/precipitation</center><br/>"
        f"<center>/api/v1.0/stations</center><br/>"
        f"<center>/api/v1.0/tobs</center><br/>"
        f"<center>/api/v1.0/start/end</center><br/>"
    )

################################################

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")

def precipitation():
    
    # Calculate the date one year from the most recent date in the dataset
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = (pd.to_datetime(most_recent_date[0]) - pd.DateOffset(days=365)).date()

    # Perform a query to retrieve the precipitation data for the last 12 months
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    session.close()

    # For each tuple in the precipitation_data list, the loop iterates through and assigns the date value as the key and the prcp value as the corresponding value in the dictionary. This process is repeated for each tuple in the list, effectively creating a dictionary where each date is paired with its respective precipitation value.
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    # Return the JSON representation of the dictionary
    return jsonify(precipitation_dict)


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")

def stations():
    
    # Query the list of unique station names from the measurement table.
    station_list = session.query(Measurement.station).distinct().all()
    
    session.close()

    # Convert the list of tuples to a list of station names
    stations = list(np.ravel(station_list))
    
    # Returns jsonified data of all of the stations in the database
    return jsonify(stations)


#Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route("/api/v1.0/tobs")

def temperatures():
    
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    previousYear = (pd.to_datetime(most_recent_date[0]) - pd.DateOffset(days=365)).date()

    results = session.query(Measurement.tobs).\
                filter(Measurement.station == 'USC00519281').\
                filter(Measurement.date >= previousYear).all()
    
    session.close
    
    temp_list = list(np.ravel(results))

    # Return a JSON list of temperature observations for the previous year.
    return jsonify(temp_list)


# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
@app.route("/api/v1.0/<start>")
@app.route('/api/v1.0/<start>/<end>')
def dateStats(start=None, end=None):
    
    #Select Statement
    selection = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    if not end:
        startDate = dt.datetime.strptime(start, "%m%d%Y")

        temp_stats = session.query(*selection).\
        filter(Measurement.date >= startDate).all()
    
        session.close
        
        temperaturelist = list(np.ravel(temp_stats))

        return jsonify(temperaturelist)
    
    else:
        startDate = dt.datetime.strptime(start, "%m%d%Y")
        endDate = dt.datetime.strptime(end, "%m%d%Y")

        temp_stats = session.query(*selection).\
        filter(Measurement.date >= startDate).\
        filter(Measurement.date <= endDate).all()

        session.close
        
        temperaturelist = list(np.ravel(temp_stats))

        return jsonify(temperaturelist)
