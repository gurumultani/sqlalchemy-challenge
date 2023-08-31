from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import func
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Create a Flask app
app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

 #Reflect the database tables into Python classes
Base = automap_base()
Base.prepare(engine)

# Creating our session (link) from Python to the DB
session = Session(engine)
# Assign the classes to variables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Define the route for the homepage
@app.route("/")
def homepage():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"Temperature Ranges:<br/>"
        f"Specify start date (YYYY-MM-DD):<br/>"
        f"<a href='/api/v1.0/start_date'>/api/v1.0/start_date</a><br/>"
        f"Specify start and end date (YYYY-MM-DD/YYYY-MM-DD):<br/>"
        f"<a href='/api/v1.0/start_date/end_date'>/api/v1.0/start_date/end_date</a>"
    )

# Define the route for precipitation data
@app.route("/api/v1.0/precipitation")

def precipitation():
    # Query the most recent date from your database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    # Calculate the date one year ago from the most recent date
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    
    # Convert results to a dictionary with date as key and prcp as value
    precipitation_data = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_data)

# Define the route for station data
@app.route("/api/v1.0/stations")
def stations():
    # Query the list of stations
    station_list = session.query(Station.station).all()
    
    # Convert the results to a list
    stations = [station[0] for station in station_list]
    
    return jsonify(stations)

# Define the route for temperature observations


@app.route("/api/v1.0/tobs")
def tobs():
    # Query the most recent date from your database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()

    # Calculate one year ago from the most recent date
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query temperature observations for the most active station over the past 12 months
    temperature_data_12_months = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= one_year_ago).all()

    # Create a list of dictionaries for the temperature data
    temperature_list = [{"Date": date, "Temperature": tobs} for date, tobs in temperature_data_12_months]

    # Return the data as JSON
    return jsonify(temperature_list)


# Route to calculate temperature stats from a start date to the end of the dataset
@app.route("/api/v1.0/<start>")
def temperature_stats_start(start):
    try:
        # Attempt to parse the start date from the URL parameter
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        
        # Query for temperature statistics from start_date to the end of the dataset
        results = session.query(func.min(Measurement.tobs).label("TMIN"),
                                func.avg(Measurement.tobs).label("TAVG"),
                                func.max(Measurement.tobs).label("TMAX"))\
            .filter(Measurement.date >= start_date)\
            .all()
        
        # Convert the results to a dictionary
        temperature_stats = {
            "TMIN": results[0].TMIN,
            "TAVG": results[0].TAVG,
            "TMAX": results[0].TMAX
        }
        
        # Return the temperature statistics as JSON
        return jsonify(temperature_stats)
    
    except ValueError:
        # Handle the case where the date parameter is not in the expected format
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD format."}), 400

# Route to calculate temperature stats from start date to end date
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats_start_end(start, end):
    try:
        # Attempt to parse start and end dates from the URL parameters
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')
        
        # Query for temperature statistics from start_date to end_date
        results = session.query(func.min(Measurement.tobs).label("TMIN"),
                                func.avg(Measurement.tobs).label("TAVG"),
                                func.max(Measurement.tobs).label("TMAX"))\
            .filter(Measurement.date >= start_date, Measurement.date <= end_date)\
            .all()
        
        # Convert the results to a dictionary
        temperature_stats = {
            "TMIN": results[0].TMIN,
            "TAVG": results[0].TAVG,
            "TMAX": results[0].TMAX
        }
        
        # Return the temperature statistics as JSON
        return jsonify(temperature_stats)
    
    except ValueError:
        # Handle the case where the date parameters are not in the expected format
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD format."}), 400
    

        
# Run the Flask app
if __name__ == "__main__":
    app.run(port=5001, debug=True)
