from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db


student_routes = Blueprint('student_routes', __name__)

@student_routes.route('/students/<int:student_id>/jobs', methods=['GET'])
def get_available_jobs(student_id):
    """
    Retrieve a list of job postings available for the student.
    """
    try:
        db = get_db()
        cursor = db.cursor()
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

@student_routes.route('/students/<int:student_id>/apply', methods=['POST'])
def apply_to_job(student_id):
    """
    Apply to a specific job posting.
    """
    try:
        data = request.get_json()
        job_posting_id = data.get('job_posting_id')
        if not job_posting_id:
            return jsonify({'error': 'Job posting ID is required'}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO Application (student_id, job_posting_id, status)
            VALUES (%s, %s, 'Pending')
        """, (student_id, job_posting_id))
        db.commit()
        return jsonify({'message': 'Application submitted successfully'}), 201
    except Exception as e:
        return jsonify({'error': f'Failed to apply for job: {str(e)}'}), 500
