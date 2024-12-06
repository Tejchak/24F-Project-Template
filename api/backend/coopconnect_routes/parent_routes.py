from flask import Blueprint, request, jsonify, make_response
from backend.db_connection import db

# Create a new blueprint for parent-related routes
parent = Blueprint('Parent', __name__)

@parent.route('/housing', methods=['GET'])
def get_housing():
    cursor = db.get_db().cursor()
    cursor.execute('SELECT * FROM Housing')
    housing_data = cursor.fetchall()
    return jsonify(housing_data), 200

@parent.route('/housing', methods=['POST'])
def insert_housing():
    data = request.get_json()
    required_keys = ['City_Name', 'zipID', 'Address', 'Rent', 'Sq_Ft']
    
    if not all(key in data for key in required_keys):
        return jsonify({"error": "Missing data"}), 400
    
    # Fetch the City_ID based on the provided City_Name
    cursor = db.get_db().cursor()
    cursor.execute('SELECT City_ID FROM City WHERE Name = %s', (data['City_Name'],))
    city_result = cursor.fetchone()
    
    if not city_result:
        return jsonify({"error": "City not found"}), 404
    
    city_id = city_result['City_ID']  # Get the City_ID from the result

    query = '''
    INSERT INTO Housing (City_ID, zipID, Address, Rent, Sq_Ft) 
    VALUES (%s, %s, %s, %s, %s)
    '''
    args = (city_id, data['zipID'], data['Address'], data['Rent'], data['Sq_Ft'])
    
    cursor = db.get_db().cursor()
    try:
        cursor.execute(query, args)
        db.get_db().commit()
        return jsonify({"success": True, "message": "Housing added successfully"}), 201
    except Exception as e:
        db.get_db().rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500

@parent.route('/housing/<int:housing_id>', methods=['PUT'])
def update_housing(housing_id):
    data = request.get_json()
    required_keys = ['City_Name', 'zipID', 'Address', 'Rent', 'Sq_Ft']
    
    if not all(key in data for key in required_keys):
        return jsonify({"error": "Missing data"}), 400
    
    # Fetch the City_ID based on the provided City_Name
    cursor = db.get_db().cursor()
    cursor.execute('SELECT City_ID FROM City WHERE Name = %s', (data['City_Name'],))
    city_result = cursor.fetchone()
    
    if not city_result:
        return jsonify({"error": "City not found"}), 404
    
    city_id = city_result['City_ID']  # Get the City_ID from the result

    query = '''
    UPDATE Housing
    SET City_ID = %s, zipID = %s, Address = %s, Rent = %s, Sq_Ft = %s
    WHERE Housing_ID = %s
    '''
    args = (city_id, data['zipID'], data['Address'], data['Rent'], data['Sq_Ft'], housing_id)
    
    cursor = db.get_db().cursor()
    try:
        cursor.execute(query, args)
        db.get_db().commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Housing not found"}), 404
        return jsonify({"success": True, "message": "Housing updated successfully"}), 200
    except Exception as e:
        db.get_db().rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500


#Deletes a specific Housing listing given the Housing_ID
@parent.route('/housing/<int:housing_id>', methods=['DELETE'])
def delete_housing_post(housing_id):
    cursor = db.get_db().cursor()
    cursor.execute('''
        DELETE FROM Housing
        WHERE Housing_ID = %s
    ''', (housing_id,))
    
    db.get_db().commit()  # Commit the transaction
    
    if cursor.rowcount > 0:
        return make_response(jsonify({'message': 'Housing deleted successfully'}), 200)
    else:
        return make_response(jsonify({'error': 'Housing listing not found'}), 404)
    
@parent.route('/hospitals/<string:city_name>', methods=['GET'])
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
    
@parent.route('/cities/<string:city_name>/safety_rating', methods=['GET'])
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
    
@parent.route('/airports', methods=['GET'])
def get_airports():
    cursor = db.get_db().cursor()
    cursor.execute('SELECT * FROM Airport')
    airport_data = cursor.fetchall()
    return jsonify(airport_data), 200

@parent.route('/hospitals', methods=['GET'])
def get_hospitals():
    cursor = db.get_db().cursor()
    cursor.execute('SELECT * FROM Hospital')
    hospital_data = cursor.fetchall()
    return jsonify(hospital_data), 200