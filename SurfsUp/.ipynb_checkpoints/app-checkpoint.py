from flask import Flask, jsonify
app = Flask(__name__)

# Define routes
@app.route("/")
def home():
    """Homepage"""
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last 12 months"""
    # Calculate the date one year ago from the last date in dataset
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query precipitation data for the last 12 months
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    # Query all stations
    stations = session.query(Station.station).all()
    
    # Convert the query results to a list
    station_list = [station for station, in stations]
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations for the most active station for the previous year"""
    # Find the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]
    
    # Calculate the date one year ago from the last date in dataset
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query temperature observations for the most active station for the previous year
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a list of dictionaries
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in tobs_data]
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return minimum, average, and maximum temperatures for all dates greater than or equal to the start date"""
    # Query temperature data for dates greater than or equal to the start date
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    # Convert the query results to a list of dictionaries
    temp_list = [{"Min Temp": temp[0], "Avg Temp": temp[1], "Max Temp": temp[2]} for temp in temp_data]
    
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return minimum, average, and maximum temperatures for dates between the start and end dates"""
    # Query temperature data for dates between the start and end dates
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    # Convert the query results to a list of dictionaries
    temp_list = [{"Min Temp": temp[0], "Avg Temp": temp[1], "Max Temp": temp[2]} for temp in temp_data]
    
    return jsonify(temp_list)

if __name__ == "__main__":
    app.run(debug=True)
