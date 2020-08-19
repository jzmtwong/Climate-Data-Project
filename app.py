# setup

# dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

# engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Database reflection
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save table references
measurement = Base.classes.measurement
Station = Base.classes.station

# Create session
session = Session(engine)

# import flask
from flask import Flask, jsonify

# Setup Flask
app = Flask(__name__)


# Routes: List flask routes that are available:
@app.route("/")
def main():
    """Home Page.  All routes that are available listed below."""
    return (
        f'All Available Routes Below:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/(input starting date)<br/>'
        f'/api/v1.0/(input starting date)/(input ending date)'
    )


# Convert query results dictionary using date = key and prcp = value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
# create function
def precipication():
    # find the max date of the database (latest date)
    max_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

    # find the exact date, and calculate 1 year back from then
    end_date = dt.datetime.strptime(max_date[0], '%Y-%m-%d')
    one_yr_ago = end_date - dt.timedelta(days=(365))

    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query((measurement.date), measurement.prcp). \
        filter((measurement.date) >= one_yr_ago).all()

    # Create dictionary to store data
    precipitation_dict = {}

    # for loop to add in all items
    for item in precipitation_data:
        precipitation_dict[item[0]] = item[1]
    return jsonify(precipitation_dict)


# return list of all stations
@app.route("/api/v1.0/stations")
def station_list():
    """Return list of all stations from the dataset, and optionally attributes."""

    # query stations list
    all_stations = session.query(Station).all()

    # create a list and jsonify
    # optionally, can remove #'s and have full list of station names and attributes
    stations_list = []
    for item in all_stations:
        station_dict = {}
        station_dict["name"] = item.name
        # station_dict["id"] = item.id
        # station_dict["station"] = item.station
        # station_dict["latitude"] = item.latitude
        # station_dict["longitude"] = item.longitude
        # station_dict["elevation"] = item.elevation
        stations_list.append(station_dict)

    return jsonify(stations_list)


# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.

# temp page
@app.route('/api/v1.0/tobs')
def tobs_yr():
    """Return list of temperature observations of the most active station for the last year."""

    # find the max date of the database (latest date)
    max_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

    # find the exact date, and calculate 1 year back from then
    end_date = dt.datetime.strptime(max_date[0], '%Y-%m-%d')
    one_yr_ago = end_date - dt.timedelta(days=(365))

    # determine the most active station
    most_active_station = (session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first())
    # record station name and query information:
    station_name = most_active_station[0]

    # request data with the above variables
    temp_data = session.query(measurement.date, measurement.tobs). \
        filter(measurement.station == station_name).filter(measurement.date >= one_yr_ago).all()

    # create jsonified list of temperatures
    temp_list = []
    name_dict = {'station_name': station_name}
    temp_list.append(name_dict)
    for item in temp_data:
        tobs_dict = {}
        tobs_dict["date"] = item.date
        tobs_dict["tobs"] = item.tobs
        temp_list.append(tobs_dict)
    return jsonify(temp_list)

#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")
def starter(start):
    """Return list of temperature observations with start date input in this format: %Y-%m-%d."""
    #First we find the last date in the database
    max_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    end_date = dt.datetime.strptime(max_date[0], '%Y-%m-%d')

    #get the temperatures
    temps = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)). \
        filter(measurement.date >= start).filter(measurement.date <= end_date).all()

    #create a list
    date_list = []
    date_dict = {'start_date': start, 'end_date': max_date}
    date_list.append(date_dict)
    date_list.append({'TMIN': temps[0][0]})
    date_list.append({'TAVG': temps[0][1]})
    date_list.append({'TMAX': temps[0][2]})

    return jsonify(date_list)

@app.route("/api/v1.0/<start>/<end>")

def date_set(start,end):
    """Return list of temperature observations with start date and end date input in this format: %Y-%m-%d."""
    #get the temperatures
    temps = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)). \
        filter(measurement.date >= start).filter(measurement.date <= end).all()

    #create the list
    date_list = []
    date_dict = {'start_date': start, 'end_date': end}
    date_list.append(date_dict)
    date_list.append({'TMIN': temps[0][0]})
    date_list.append({'TAVG': temps[0][1]})
    date_list.append({'TMAX': temps[0][2]})

    return jsonify(date_list)




# Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
