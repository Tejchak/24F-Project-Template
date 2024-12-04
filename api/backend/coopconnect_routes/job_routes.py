from flask import Blueprint  # To define the blueprint for organizing your routes.
from flask import request    # To handle incoming request data (useful for POST/PUT routes).
from flask import jsonify    # To convert Python dictionaries/lists to JSON responses.
from flask import make_response  # To structure the HTTP response with status codes.
from flask import current_app  # To access the Flask application context if needed.
from backend.db_connection import db  # To interact with your database connection object.


@performance.route('/jobs', methods=['GET'])
def get_all_jobs():
    cursor = db.get_db().cursor()
    query = "SELECT * FROM Job"
    cursor.execute(query)
    theData = cursor.fetchall()

    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response

@performance.route('/job_postings/location/<Location_ID>', methods=['GET'])
def get_job_postings_by_location(Location_ID):
    cursor = db.get_db().cursor()
    query = """
    SELECT Post_ID, Compensation, User_ID
    FROM JobPosting
    WHERE Location_ID = %s
    """
    cursor.execute(query, (Location_ID,))
    theData = cursor.fetchall()

    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response
