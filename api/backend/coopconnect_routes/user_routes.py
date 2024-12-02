from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db


#Creates a new blueprint to collect the routes
users = Blueprint('Users', __name__)



#Return a list of all users with their respective information
@users.route('/user', methods=['GET'])
def get_users():

    cursor = db.get_db().cursor()
    cursor.execute('SELECT * FROM User')
                   
    
    theData = cursor.fetchall()
    
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response

#Update the information of a specific user.
@users.route('/user/<UserID>', methods=['PUT'])
def update_user(UserID):

    cursor = db.get_db().cursor()
    cursor.execute('UPD')
                   
    
    theData = cursor.fetchall()
    
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response