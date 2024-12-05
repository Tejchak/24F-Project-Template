from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db

#Creates a new blueprint to collect the routes
locations = Blueprint('location', __name__)


#Returns all locations with details about each city
@locations.route('/location', methods=['GET'])
def get_all_locations():
    cursor = db.get_db().cursor
    cursor.execute('SELECT * FROM Locations')
    
    theData = cursor.fetchall()
    
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response


#Returns the details of a specific city
locations.route('/location/<Zip>', methods=['GET'])
def get_location_details(Zip):
    try:
        query = '''
        SELECT Zip, City_ID, Student_pop, Safety_Rating
        FROM Location
        '''
        cursor = db.get_db().cursor()
        cursor.execute(query, (Zip))
        theData = cursor.fetchall()
        
        return make_response(jsonify(theData), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

#Returns the safety rating of a specific city
@locations.route('/location/safety/<City_ID>', methods=['GET'])
def get_safety_rating(City_ID):
    try:
        query = '''
        SELECT City_ID, Safety_Rating
        FROM Locations
        WHERE City_ID = %s
        '''
        cursor = db.get_db().cursor()
        cursor.execute(query, (City_ID,))
        theData = cursor.fetchone()
        if theData:
            return make_response(jsonify(theData), 200)
        else:
            return make_response(jsonify({"error": "City_ID not found"}), 404)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
    