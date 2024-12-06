from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db
from flask import Blueprint, request, jsonify, abort
from datetime import datetime
from backend.db_connection import db

# Create a blueprint for housing-related routes
housing = Blueprint('housing', __name__)

@housing.route('/sublets/dates', methods=['GET'])
def get_sublets_by_date():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    student_id = request.args.get('student_id')  # Optional parameter

    if not start_date or not end_date:
        abort(400, description="Missing start_date or end_date parameters")

    try:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        if start_datetime > end_datetime:
            abort(400, description="start_date must be before end_date")
    except ValueError:
        abort(400, description="Invalid date format. Please use YYYY-MM-DD format.")

    try:
        cursor = db.get_db().cursor()

        if student_id:
            # Validate student existence
            cursor.execute('SELECT 1 FROM User WHERE UserID = %s', (student_id,))
            if not cursor.fetchone():
                abort(404, description="Student not found")

            # Query sublets for the specific student
            cursor.execute('''
                SELECT S.*
                FROM Sublet S
                JOIN User U ON S.Subleter_ID = U.UserID
                WHERE U.CategoryID = (
                    SELECT CategoryID FROM Category WHERE CategoryName = 'Student'
                )
                  AND S.Start_Date >= %s AND S.End_Date <= %s
                  AND S.Subleter_ID = %s
            ''', (start_date, end_date, student_id))
        else:
            # Query sublets for all students
            cursor.execute('''
                SELECT S.*
                FROM Sublet S
                JOIN User U ON S.Subleter_ID = U.UserID
                WHERE U.CategoryID = (
                    SELECT CategoryID FROM Category WHERE CategoryName = 'Student'
                )
                  AND S.Start_Date >= %s AND S.End_Date <= %s
            ''', (start_date, end_date))

        sublets = cursor.fetchall()
        if not sublets:
            return jsonify({'message': 'No sublets found for the given date range'}), 404

        return jsonify(sublets), 200

    except Exception as e:
        abort(500, description=str(e))
