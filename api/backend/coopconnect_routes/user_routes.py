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

    query = '''
    UPDATE 
    User SET CategoryID = (SELECT CategoryID FROM Category WHERE CategoryName = 'Student') 
    WHERE UserID = {0}'''.format(UserID)
    '''
    '''

    cursor = db.get_db().cursor()
    cursor.execute(query)
    db.get_db.commit
                   
    return 'user updated!'


#Returns information about students in a specific city
@users.route('/user/<CityID>/<Category_ID>', methods=['GET'])
def get_users(CityID,Category_ID):

    query = '''
        SELECT * FROM User
        Where {0}'''.format(CityID)
    ''' AND '''.format(Category_ID)
    '''(SELECT CategoryID FROM Category WHERE CategoryName = 'Student')
        '''

    cursor = db.get_db().cursor()
    cursor.execute('SELECT * FROM User')
                   
    
    theData = cursor.fetchall()
    
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response