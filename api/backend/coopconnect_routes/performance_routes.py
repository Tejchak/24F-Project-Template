from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db


#Creates a new blueprint to collect the routes
performance = Blueprint('Performance', __name__)



#Get all performance info from the system on a given day
@performance.route('/performance/<Date>', methods=['GET'])
def get_performance(Date):

    cursor = db.get_db().cursor()
    cursor.execute('SELECT * FROM Performance WHERE PID = {0}'.format(Date))
                   
    
    theData = cursor.fetchall()
    
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response