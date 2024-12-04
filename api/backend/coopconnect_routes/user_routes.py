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

@users.route('/user/<int:UserID>', methods=['PUT'])
def update_user(UserID):
    try:
        # Extract data from the request body
        data = request.json
        category_id = data.get('CategoryID')
        name = data.get('name')
        email = data.get('email')
        phone_number = data.get('Phone_Number')

        query = '''
        UPDATE User 
        SET CategoryID = %s, name = %s, email = %s, Phone_Number = %s
        WHERE UserID = %s
        '''
        cursor = db.get_db().cursor()
        cursor.execute(query, (category_id, name, email, phone_number, UserID))
        db.get_db().commit()

        return make_response(jsonify({"message": "User updated successfully!"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)



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

@users.route('/users/<int:CityID>/students', methods=['GET'])
def get_students_in_city(CityID):
    try:
        query = '''
        SELECT U.UserID, U.name, U.email 
        FROM User U
        WHERE U.Current_City_ID = %s 
          AND U.CategoryID = (SELECT CategoryID FROM Category WHERE CategoryName = 'Student')
        '''
        cursor = db.get_db().cursor()
        cursor.execute(query, (CityID,))
        theData = cursor.fetchall()

        return make_response(jsonify(theData), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
