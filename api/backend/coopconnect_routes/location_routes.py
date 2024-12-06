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


@locations.route('/cities/<string:city_name>/safety_rating', methods=['GET'])
def get_safety_rating_by_zip(city_name):
    cursor = db.get_db().cursor()
    cursor.execute('''
        SELECT L.Zip, L.Safety_Rating
        FROM Location L
        WHERE L.City_ID = (SELECT City_ID FROM City WHERE Name = %s)
    ''', (city_name,))
    
    safety_rating_data = cursor.fetchall()  # Fetch all results
    print(safety_rating_data)
    
    if safety_rating_data:
        result = [{'Zip': row['Zip'], 'Safety_Rating': row['Safety_Rating']} for row in safety_rating_data]
        return make_response(jsonify(result), 200)
    else:
        return "No zipcodes for selected city", 404



      

