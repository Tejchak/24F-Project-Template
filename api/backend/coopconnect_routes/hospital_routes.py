from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db

# Create a new blueprint for hospital routes
hospitals = Blueprint('hospitals', __name__)

#Returns hospitals for a given City_ID
@hospitals.route('/hospitals/<City_ID>', methods=['GET'])
def get_hospitals_by_city(City_ID):
    try:
        query = '''
        SELECT HospitalID, Name, City_ID, Zip
        FROM Hospital
        WHERE City_ID = %s
        '''
        cursor = db.get_db().cursor()
        cursor.execute(query, (City_ID,))
        hospital_data = cursor.fetchall()

        # Check if any hospitals were found
        if hospital_data:
            return make_response(jsonify(hospital_data), 200)
        else:
            return make_response(jsonify({"message": "No hospitals found for the given City_ID"}), 404)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
    


@hospitals.route('/hospitals', methods=['GET'])
def get_hospitals():
    cursor = db.get_db().cursor()
    cursor.execute('SELECT * FROM Hospital')
    hospital_data = cursor.fetchall()
    return jsonify(hospital_data), 200