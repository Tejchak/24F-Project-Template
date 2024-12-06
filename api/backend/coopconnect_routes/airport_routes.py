from flask import Blueprint, request, jsonify
from backend.db_connection import db

airports = Blueprint('Airport', __name__)

@airports.route('/airports', methods=['GET'])
def get_airports():
    cursor = db.get_db().cursor()
    cursor.execute('SELECT * FROM Airport')
    airport_data = cursor.fetchall()
    return jsonify(airport_data), 200
