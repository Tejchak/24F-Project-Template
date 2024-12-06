from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db

# Create a new blueprint for hospital routes
hospitals = Blueprint('hospitals', __name__)

#Returns hospitals for a given City_ID
@hospitals.route('/hospitals/<string:city_name>', methods=['GET'])
def get_hospitals_by_city(city_name):
    try:
        # First, get the City_ID based on the city name
        query_city_id = '''
        SELECT City_ID FROM City WHERE Name = %s
        '''
        cursor = db.get_db().cursor()
        cursor.execute(query_city_id, (city_name,))
        city_id_result = cursor.fetchone()

        if not city_id_result:
            return make_response(jsonify({"message": "City not found"}), 404)

        city_id = city_id_result['City_ID']

        # Now, get the hospitals using the City_ID
        query_hospitals = '''
        SELECT HospitalID, Name, City_ID, Zip
        FROM Hospital
        WHERE City_ID = %s
        '''
        cursor.execute(query_hospitals, (city_id,))
        hospital_data = cursor.fetchall()

        # Check if any hospitals were found
        if hospital_data:
            return make_response(jsonify(hospital_data), 200)
        else:
            return make_response(jsonify({"message": "No hospitals found for the given city name"}), 404)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
    


@hospitals.route('/hospitals', methods=['GET'])
def get_hospitals():
    cursor = db.get_db().cursor()
    cursor.execute('SELECT * FROM Hospital')
    hospital_data = cursor.fetchall()
    return jsonify(hospital_data), 200