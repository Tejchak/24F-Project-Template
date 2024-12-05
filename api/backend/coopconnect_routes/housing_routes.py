from flask import Blueprint, request, jsonify
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
def add_housing():
    data = request.get_json()
    if not all(key in data for key in ['City_ID', 'zipID', 'Address', 'Rent', 'Sq_Ft']):
        return jsonify({"error": "Missing data"}), 400
    
    query = '''
    INSERT INTO Housing (City_ID, zipID, Address, Rent, Sq_Ft) 
    VALUES (%s, %s, %s, %s, %s)
    '''
    args = (data['City_ID'], data['zipID'], data['Address'], data['Rent'], data['Sq_Ft'])
    
    cursor = db.get_db().cursor()
    try:
        cursor.execute(query, args)
        db.get_db().commit()
        return jsonify({"success": True, "message": "Housing added successfully"}), 201
    except Exception as e:
        db.get_db().rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500

