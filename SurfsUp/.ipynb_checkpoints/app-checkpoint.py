# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


#################################################
# Database Setup
#################################################

# create a reference to the dataset

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

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
def Homepage():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
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

    # For each tuple in the precipitation_data list, the loop iterates through and assigns the date value as the key and the prcp value as the corresponding value in the dictionary. This process is repeated for each tuple in the list, effectively creating a dictionary where each date is paired with its respective precipitation value.
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    # Return the JSON representation of the dictionary
    return jsonify(precipitation_dict)


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")

def stations():
    
    # Query the list of unique station names from the measurement table.
    station_list = session.query(Measurement.station).distinct().all()
    
    # Convert the list of tuples to a list of station names
    stations = [station[0] for station in station_list]
    
    # Returns jsonified data of all of the stations in the database
    return jsonify(stations)


#Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route("/api/v1.0/tobs")

def tobs():
    
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = (pd.to_datetime(most_recent_date[0]) - pd.DateOffset(days=365)).date()

    # Define the columns to select and join the Measurement and Station tables.
    sel = [Measurement.date, Measurement.tobs]
    
    # Query the dates and temperature observations of the most-active station for the previous year of data.
    tobs_query = session.query(*sel).\
        join(Station, Measurement.station == Station.station).\
        filter(Measurement.date >= one_year_ago).\
        filter(Station.station == "USC00519281").all()
    
    # Extracts the temperature observations (TOBs) from the query results and stores them in a list.
    tobs_data = [result[1] for result in tobs_query]

    # Return a JSON list of temperature observations for the previous year.
    return jsonify(tobs_data)


# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
@app.route("/api/v1.0/<start>")
def start_date(start):
    
    # Convert the input start date to a datetime object
    start_date = pd.to_datetime(start).date()

    # Query to calculate TMIN, TAVG, and TMAX for dates greater than or equal to the start date
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()


    # Create a list to store the temperature statistics
    temp_data_start = [temp_stats[0][0], temp_stats[0][1], temp_stats[0][2]]

    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for start date
    return jsonify(temp_data_start)


# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route('/api/v1.0/<start>/<end>')
def start_end_date(start, end):
    
    # Convert the input start and end dates to datetime objects
    start_date = pd.to_datetime(start).date()
    end_date = pd.to_datetime(end).date()

    # Query to calculate TMIN, TAVG, and TMAX for dates between start date and end date (inclusive)
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
        
    # Create a list to store the temperature statistics
    temp_data_start_end = [temp_stats[0][0], temp_stats[0][1], temp_stats[0][2]]


    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for start/end date
    return jsonify(temp_data_start_end)

# Check if the script is being run directly (not imported as a module)
# and if so, start the Flask app in debug mode.
if __name__ == "__main__":
    app.run(debug=True)
