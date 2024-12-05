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
    cursor.execute('SELECT * FROM User JOIN Category ON User.CategoryID = Category.CategoryID')
                   
    
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

@users.route('/users/city/<int:CityID>/category/<string:CategoryName>', methods=['GET'])
def get_users_by_city_and_category(CityID, CategoryName):
    try:
        query = '''
        SELECT U.UserID, U.name, U.email, U.Phone_Number 
        FROM User U
        JOIN Category C ON U.CategoryID = C.CategoryID
        WHERE U.Current_City_ID = %s AND C.CategoryName = %s
        '''
        cursor = db.get_db().cursor()
        cursor.execute(query, (CityID, CategoryName))
        theData = cursor.fetchall()

        return make_response(jsonify(theData), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

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

#Retrieves specific user using UserID
@users.route('/user/<int:UserID>', methods=['GET'])
def get_user_by_id(UserID):
    try:
        query = 'SELECT * FROM User WHERE UserID = %s'
        cursor = db.get_db().cursor()
        cursor.execute(query, (UserID,))
        theData = cursor.fetchone()

        if not theData:
            return make_response(jsonify({"error": "User not found"}), 404)

        return make_response(jsonify(theData), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

#Delete a user by ID
@users.route('/user/<int:UserID>', methods=['DELETE'])
def delete_user(UserID):
    try:
        query = 'DELETE FROM User WHERE UserID = %s'
        cursor = db.get_db().cursor()
        cursor.execute(query, (UserID,))
        db.get_db().commit()

        if cursor.rowcount == 0:
            return make_response(jsonify({"error": "User not found"}), 404)

        return make_response(jsonify({"message": "User deleted successfully!"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

#Get user by cityID
@users.route('/users/<int:CityID>', methods=['GET'])
def get_users_in_city(CityID):
    try:
        query = 'SELECT * FROM User WHERE Current_City_ID = %s'
        cursor = db.get_db().cursor()
        cursor.execute(query, (CityID,))
        theData = cursor.fetchall()

        return make_response(jsonify(theData), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

@users.route('/users/search', methods=['GET'])
def search_users():
    try:
        search_query = request.args.get('query', '')
        query = '''
        SELECT UserID, name, email, Phone_Number 
        FROM User
        WHERE name LIKE %s OR email LIKE %s
        '''
        cursor = db.get_db().cursor()
        cursor.execute(query, (f"%{search_query}%", f"%{search_query}%"))
        theData = cursor.fetchall()

        return make_response(jsonify(theData), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

@users.route('/users/category/<string:CategoryName>', methods=['GET'])
def get_users_by_category(CategoryName):
    try:
        query = '''
        SELECT U.UserID, U.name, U.email, U.Phone_Number 
        FROM User U
        JOIN Category C ON U.CategoryID = C.CategoryID
        WHERE C.CategoryName = %s
        '''
        cursor = db.get_db().cursor()
        cursor.execute(query, (CategoryName,))
        theData = cursor.fetchall()

        return make_response(jsonify(theData), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

@users.route('/users/created-after/<string:date>', methods=['GET'])
def get_users_created_after(date):
    try:
        query = '''
        SELECT UserID, name, email, Phone_Number, Date_Created 
        FROM User 
        WHERE Date_Created > %s
        '''
        cursor = db.get_db().cursor()
        cursor.execute(query, (date,))
        theData = cursor.fetchall()

        return make_response(jsonify(theData), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

@users.route('/users/email/<string:email>', methods=['GET'])
def get_user_by_email(email):
    try:
        query = '''
        SELECT UserID, name, Phone_Number, Date_Created, Date_Last_Login 
        FROM User 
        WHERE email = %s
        '''
        cursor = db.get_db().cursor()
        cursor.execute(query, (email,))
        theData = cursor.fetchone()

        if not theData:
            return make_response(jsonify({"error": "User not found"}), 404)

        return make_response(jsonify(theData), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
