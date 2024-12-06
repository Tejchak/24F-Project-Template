from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from datetime import datetime
from flask import abort
from backend.db_connection import db

student = Blueprint('student_routes', __name__)

@student.route('/students/<int:student_id>/jobs', methods=['GET'])
def get_available_jobs(student_id):
    """
    Retrieve a list of job postings available for the student.
    """
    try:
        cursor = db.get_db().cursor()
        cursor.execute("""
            SELECT * FROM JobPosting 
            WHERE job_posting_id NOT IN (
                SELECT job_posting_id 
                FROM Application 
                WHERE student_id = %s
            )
        """, (student_id,))
        jobs = cursor.fetchall()
        
        if not jobs:
            return jsonify({'message': 'No available jobs found'}), 404
        
        return jsonify(jobs), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve jobs: {str(e)}'}), 500
    

@student.route('/students/<int:student_id>', methods=['PUT'])
def update_student_profile(student_id):
    """
    Update the student's profile information.
    """
    try:
        data = request.get_json()
        cursor = db.get_db().cursor()
        cursor.execute("""
            UPDATE User 
            SET name = %s, email = %s, Phone_Number = %s, CategoryID = %s
            WHERE UserID = %s
        """, (
            data.get('name'),
            data.get('email'),
            data.get('phone_number'),
            data.get('CategoryID', 1),  # Default to CategoryID 1 if not provided
            student_id
        ))
        db.get_db().commit()
        
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500
    
@student.route('/students/<int:student_id>/sublet', methods=['POST'])
def create_sublet(student_id):
    try:
        data = request.json
        housing_id = data.get('Housing_ID')
        start_date = data.get('Start_Date')
        end_date = data.get('End_Date')

        query = '''
        INSERT INTO Sublet (Housing_ID, Subleter_ID, Start_Date, End_Date)
        VALUES (%s, %s, %s, %s)
        '''
        cursor = db.get_db().cursor()
        cursor.execute(query, (housing_id, student_id, start_date, end_date))
        db.get_db().commit()

        return make_response(jsonify({"message": "Sublet created successfully!"}), 201)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


@student.route('/sublets/<int:sublet_id>', methods=['PUT'])
def update_sublet(sublet_id):
    """
    Update details of a sublet.
    """
    try:
        # Get data from the request body
        data = request.get_json()

        # Validate the presence of necessary fields
        required_fields = ['title', 'description', 'rent', 'address', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data:
                abort(400, description=f"Missing required field: {field}")

        # Validate dates
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
            if start_date > end_date:
                abort(400, description="start_date must be before end_date")
        except ValueError:
            abort(400, description="Invalid date format. Please use YYYY-MM-DD format.")

        # Update sublet details in the database
        cursor = db.get_db().cursor()
        cursor.execute('''
            UPDATE Sublet
            SET Title = %s, Description = %s, Rent = %s, Address = %s, Start_Date = %s, End_Date = %s
            WHERE Sublet_ID = %s
        ''', (
            data['title'],
            data['description'],
            data['rent'],
            data['address'],
            data['start_date'],
            data['end_date'],
            sublet_id
        ))
        db.get_db().commit()

        return jsonify({'message': 'Sublet updated successfully'}), 200
    except Exception as e:
        abort(500, description=str(e))


@student.route('/sublets/<int:sublet_id>', methods=['DELETE'])
def delete_sublet(sublet_id):
    """
    Delete a sublet.
    """
    try:
        # Delete the sublet from the database
        cursor = db.get_db().cursor()
        cursor.execute('''
            DELETE FROM Sublet
            WHERE Sublet_ID = %s
        ''', (sublet_id,))
        db.get_db().commit()

        return jsonify({'message': 'Sublet deleted successfully'}), 200
    except Exception as e:
        abort(500, description=str(e))
