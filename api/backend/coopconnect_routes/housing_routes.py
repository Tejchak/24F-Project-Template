from flask import Blueprint, request, jsonify, make_response
from backend.db_connection import db

# Create a new blueprint for housing-related routes
housing = Blueprint('Housing', __name__)

@housing.route('/housing', methods=['GET'])
def get_housing():
    cursor = db.get_db().cursor()
    cursor.execute('SELECT * FROM Housing')
    housing_data = cursor.fetchall()
    return jsonify(housing_data), 200

@housing.route('/housing', methods=['POST'])
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

@housing.route('/housing/<int:housing_id>', methods=['PUT'])
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
@housing.route('/housing/<int:housing_id>', methods=['DELETE'])
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
    