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

@student_routes.route('/students/<int:student_id>/applications', methods=['GET'])
def get_application_status(student_id):
    """
    Retrieve the status of all applications submitted by the student.
    """
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT Application.*, JobPosting.title AS job_title 
            FROM Application 
            JOIN JobPosting ON Application.job_posting_id = JobPosting.job_posting_id
            WHERE Application.student_id = %s
        """, (student_id,))
        applications = cursor.fetchall()
        if not applications:
            return jsonify({'message': 'No applications found'}), 404
        return jsonify(applications), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve applications: {str(e)}'}), 500

@student_routes.route('/students/<int:student_id>/recommendations', methods=['GET'])
def get_job_recommendations(student_id):
    """
    Fetch personalized job recommendations for the student.
    """
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT * 
            FROM JobPosting 
            WHERE skills_required IN (
                SELECT skill 
                FROM StudentSkills 
                WHERE student_id = %s
            )
            AND job_posting_id NOT IN (
                SELECT job_posting_id 
                FROM Application 
                WHERE student_id = %s
            )
            LIMIT 10
        """, (student_id, student_id))
        recommendations = cursor.fetchall()
        if not recommendations:
            return jsonify({'message': 'No recommendations available'}), 404
        return jsonify(recommendations), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch recommendations: {str(e)}'}), 500

@student_routes.route('/students/<int:student_id>', methods=['PUT'])
def update_student_profile(student_id):
    """
    Update the student's profile information.
    """
    try:
        data = request.get_json()
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE Student 
            SET name = %s, email = %s, phone = %s, address = %s
            WHERE student_id = %s
        """, (
            data.get('name'),
            data.get('email'),
            data.get('phone'),
            data.get('address'),
            student_id
        ))
        db.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

from flask import Blueprint, request, jsonify, make_response
from db_connection import db

student_routes = Blueprint('student_routes', __name__)

@student_routes.route('/students/<int:student_id>/applications/<int:application_id>', methods=['DELETE'])
def delete_application(student_id, application_id):
    """
    Deletes a job application for a specific student.
    """
    cursor = db.get_db().cursor()

    try:
        # Check if the application exists and belongs to the student
        cursor.execute('''
            SELECT * FROM Application
            WHERE application_id = %s AND student_id = %s
        ''', (application_id, student_id))
        application = cursor.fetchone()

        if not application:
            return make_response(jsonify({'error': 'Application not found or does not belong to this student'}), 404)

        # Perform the deletion
        cursor.execute('''
            DELETE FROM Application
            WHERE application_id = %s
        ''', (application_id,))
        db.get_db().commit()

        # Check if the deletion was successful
        if cursor.rowcount > 0:
            return make_response(jsonify({'message': 'Application deleted successfully'}), 200)
        else:
            return make_response(jsonify({'error': 'Failed to delete application'}), 500)

    except Exception as e:
        return make_response(jsonify({'error': f'Database error: {str(e)}'}), 500)
