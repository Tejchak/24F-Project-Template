from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db
#Creates a new blueprint to collect the routes
employer = Blueprint('Employer', __name__)

# Get details for a certain city
@employer.route('/cities/<int:City_ID>', methods=['GET'])
def get_city_details(City_ID):
    cursor = db.get_db().cursor()
    cursor.execute('SELECT Name, Avg_Cost_Of_Living, Avg_Rent, Prop_Hybrid_Workers FROM City WHERE City_ID = %s', (City_ID,))
    
    city_details = cursor.fetchone()
    
    if city_details:
        the_response = make_response(jsonify({
            'City_Name': city_details[0],
            'Avg_Cost_Of_Living': city_details[1],
            'Avg_Rent': city_details[2],
            'Prop_Hybrid_Workers': city_details[3]
        }))
        the_response.status_code = 200
    else:
        the_response = make_response(jsonify({'error': 'City not found'}), 404)
    
    return the_response

# Get student population for a certain city
@employer.route('/cities/<int:City_ID>/student_population', methods=['GET'])
def get_student_population(City_ID):
    cursor = db.get_db().cursor()
    cursor.execute('''
        SELECT SUM(Student_Population) 
        FROM ZipCode 
        WHERE City_ID = %s
    ''', (City_ID,))
    
    student_population = cursor.fetchone()[0]  # Get the sum from the result
    
    if student_population is not None:
        the_response = make_response(jsonify({
            'City_ID': City_ID,
            'Student_Population': student_population
        }))
        the_response.status_code = 200
    else:
        the_response = make_response(jsonify({'error': 'City not found or no student population data'}), 404)
    
    return the_response

# Get all job postings for a specific user
@employer.route('/users/<int:user_id>/job_postings', methods=['GET'])
def get_user_job_postings(user_id):
    cursor = db.get_db().cursor()
    cursor.execute('''
        SELECT Post_ID, Compensation, Location_ID, User_ID
        FROM JobPosting
        WHERE User_ID = %s
    ''', (user_id,))
    
    job_postings = cursor.fetchall()  # Fetch all job postings for the user
    
    if job_postings:
        postings_list = []
        for posting in job_postings:
            postings_list.append({
                'Post_ID': posting[0],
                'Compensation': posting[1],
                'Location_ID': posting[2],
                'User_ID': posting[3]
            })
        return make_response(jsonify(postings_list), 200)
    else:
        return make_response(jsonify({'error': 'No job postings found for this user'}), 404)

# Delete a job posting
@employer.route('/job_postings/<int:post_id>', methods=['DELETE'])
def delete_job_posting(post_id):
    cursor = db.get_db().cursor()
    cursor.execute('''
        DELETE FROM JobPosting
        WHERE Post_ID = %s
    ''', (post_id,))
    
    db.get_db().commit()  # Commit the transaction
    if cursor.rowcount > 0:
        return make_response(jsonify({'message': 'Job posting deleted successfully'}), 200)
    else:
        return make_response(jsonify({'error': 'Job posting not found'}), 404)

# Update a job posting
@employer.route('/job_postings/<int:post_id>', methods=['PUT'])
def update_job_posting(post_id):
    data = request.get_json()  # Get the JSON data from the request
    compensation = data.get('compensation')
    location_id = data.get('location_id')

    if compensation is None and location_id is None:
        return make_response(jsonify({'error': 'No fields to update'}), 400)

    updates = []
    if compensation is not None:
        updates.append(f"Compensation = %s")
    if location_id is not None:
        updates.append(f"Location_ID = %s")

    update_query = f'''
        UPDATE JobPosting
        SET {', '.join(updates)}
        WHERE Post_ID = %s
    '''
    
    params = []
    if compensation is not None:
        params.append(compensation)
    if location_id is not None:
        params.append(location_id)
    params.append(post_id)

    cursor = db.get_db().cursor()
    cursor.execute(update_query, tuple(params))
    
    db.get_db().commit()  # Commit the transaction
    if cursor.rowcount > 0:
        return make_response(jsonify({'message': 'Job posting updated successfully'}), 200)
    else:
        return make_response(jsonify({'error': 'Job posting not found'}), 404)

# Get student population for each zipcode in a specified city
@employer.route('/cities/<string:city_name>/student_population', methods=['GET'])
def get_student_population_by_zip(city_name):
    cursor = db.get_db().cursor()
    cursor.execute('''
        SELECT L.Zip, L.Student_pop
        FROM Location L
        WHERE L.City_ID = (SELECT City_ID FROM City WHERE Name = %s)
    ''', (city_name,))
    
    student_population_data = cursor.fetchall()  # Fetch all results
    print(student_population_data)
    if student_population_data:
        result = [{'Zip': row['Zip'], 'Student_Population': row['Student_pop']} for row in student_population_data]
        return make_response(jsonify(result), 200)
    else:
        return "No zipcodes for selected city"

# Get all zip codes
@employer.route('/zipcodes', methods=['GET'])
def get_all_zipcodes():
    cursor = db.get_db().cursor()
    cursor.execute('SELECT Zip FROM Location')
    
    zipcodes = cursor.fetchall()  # Fetch all zip codes
    
    if zipcodes:
        # Convert the list of tuples to a list of zip codes
        zip_list = [zipcode['Zip'] for zipcode in zipcodes]
        return make_response(jsonify(zip_list), 200)
    else:
        return make_response(jsonify({'error': 'No zip codes found'}), 404)
    
# Create a new job posting
@employer.route('/job_postings', methods=['POST'])
def create_job_posting():
    data = request.get_json()  
    compensation = data.get('compensation')
    location_id = data.get('location_id')
    user_email = data.get('user_email')

    if not compensation or not location_id or not user_email:
        return make_response(jsonify({'error': 'Missing required fields'}), 400)

 # Fetch user ID using the provided email
    cursor = db.get_db().cursor()
    cursor.execute('''
        SELECT UserID 
        FROM User 
        WHERE email = %s
    ''', (user_email,))
    
    user_id = cursor.fetchone()  
    if not user_id:
        return make_response(jsonify({'error': 'User not found'}), 404)

    user_id = user_id['UserID']

    cursor.execute('''
        INSERT INTO JobPosting (Compensation, Location_ID, User_ID)
        VALUES (%s, %s, %s)
    ''', (compensation, location_id, user_id))

    db.get_db().commit()  
    return make_response(jsonify({'message': 'Job posting created successfully'}), 201)

