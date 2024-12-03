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
    # Retrieve dates from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Validate the date format and existence
    if not start_date or not end_date:
        abort(400, description="Missing start_date or end_date parameters")

    try:
        # Convert string dates to datetime objects to ensure valid formats
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

        # Ensure start_date is before end_date
        if start_datetime > end_datetime:
            abort(400, description="start_date must be before end_date")

    except ValueError:
        abort(400, description="Invalid date format. Please use YYYY-MM-DD format.")

    try:
        # Execute database query
        cursor = db.get_db().cursor()
        cursor.execute('''
            SELECT * FROM Sublet
            WHERE Start_Date >= %s AND End_Date <= %s
        ''', (start_date, end_date))
        sublets = cursor.fetchall()

        # Check if sublets are found
        if not sublets:
            return jsonify({'message': 'No sublets found for the given date range'}), 404

        return jsonify(sublets), 200

    except Exception as e:
        # Handle unexpected database errors
        abort(500, description=str(e))
