from flask import Blueprint, request, jsonify
from backend.db_connection import db

airports = Blueprint('Airport', __name__)

@airports.route('/airports', methods=['GET'])
def get_airports():
    cursor = db.get_db().cursor()
    cursor.execute('SELECT * FROM Airport')
    airport_data = cursor.fetchall()
    return jsonify(airport_data), 200

@airports.route('/hospitals', methods=['GET'])
def get_hospitals():
    cursor = db.get_db().cursor()
    cursor.execute('SELECT * FROM Hospital')
    hospital_data = cursor.fetchall()
    return jsonify(hospital_data), 200