#import dependencies
import numpy as np
import datetime as dt

#import sql alchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from flask import Flask, jsonify

#engine to hawaii sql lite file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base=automap_base()
# reflect the tables
base.prepare(engine, reflect=True)
# Save references to each table
measurement=base.classes.measurement
station=base.classes.station
#app
app=Flask(__name__)


#home page 
@app.route('/')
def home_page():
    print("Home page")
    return (
        f'<p>/api/v1.0/percipitation</p>'+
        f'<p>/api/v1.0/stations</p>'
        f'<p>/api/v1.0/tobs</p>'
        f'<p>/api/v1.0/start</p>'
        f'<p>/api/v1.0/start/end</p>'
        )

#perticipation Data
@app.route('/api/v1.0/percipitation')
def percipitation():
    print("percipitation")
    session = Session(engine)
    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    data = session.query(measurement.date, measurement.prcp) .\
        filter(measurement.date >= query_date).all()   
    session.close()

    # create empty dict
    precip_data = []
    #now fill the dict with data
    for date,prcp in data:
        precip_dict = {}
        precip_dict[date] = prcp
        precip_data.append(precip_dict)

    return jsonify(precip_data)


#Stations Data 
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    station_list = session.query(station.station, station.name).all()
   
    station_data = {}
    for i,name in station_list:
        station_data[i] = name
    session.close()

    return jsonify(station_data)       



@app.route('/api/v1.0/tobs')
def tobs(): 
    # Create our session (link) from Python to the DB
    session = Session(engine)

    latest_date=dt.date(2017,8,23)-dt.timedelta(days=365)

    active_station = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()

    tobs_year = session.query(measurement.date,measurement.tobs).filter(measurement.station == active_station[0][0]).\
         filter(measurement.date>=latest_date).all()

    tobs_date_list = []
    for station, tobs in tobs_year:
        new_dict = {}
        new_dict[station] = tobs
        tobs_date_list.append(new_dict)

    session.close()
    return jsonify(tobs_date_list) 

@app.route('/api/v1.0/<start>')
def start(start): 
    session = Session(engine)
    query = session.query(func.min(measurement.tobs),\
        func.avg(measurement.tobs),\
            func.max(measurement.tobs)).\
                filter(measurement.date >= start).all()
    #thanks gonzalo
    temp = list(np.ravel(query))
    start_dict = {
        "DATE": start,
        "TMIN": temp[0],
        "TAVG": temp[1],
        "TMAX": temp[2]
        }
    session.close()
    return jsonify(start_dict)
    
 

@app.route('/api/v1.0/<start>/<end>')
def start_and_end(start,end):
    session = Session(engine)
    query = session.query(func.min(measurement.tobs),\
        func.avg(measurement.tobs),\
            func.max(measurement.tobs)).\
                filter(measurement.date >= start).\
                    filter(measurement.date <= end).all()
    #thanks gonzalo
    temp = list(np.ravel(query))
    start_end_dict = {
        "START DATE": start,
        "END DATE": end,
        "TMIN": temp[0],
        "TAVG": temp[1],
        "TMAX": temp[2]
        }
    session.close()
    return jsonify(start_end_dict)


if __name__ == "__main__":
    app.run(debug=True)