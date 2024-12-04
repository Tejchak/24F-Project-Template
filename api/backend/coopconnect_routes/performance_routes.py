from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db
from datetime import datetime


#Creates a new blueprint to collect the routes
performance = Blueprint('Performance', __name__)



#Get all performance info from the system on a given day
@performance.route('/performance/<Date>', methods=['GET'])
def get_performance(Date):
    cursor = db.get_db().cursor()
    cursor.execute('SELECT * FROM Performance WHERE date(Date) = %s', (Date,))
    performance_data = cursor.fetchall()
    cursor.close()

    # Convert the data to a list of dictionaries
    formatted_data = []
    for record in performance_data:
        formatted_data.append({
            'PID': record['PID'],
            'CPU_Usage': float(record['Avg_Speed']) if record['Avg_Speed'] is not None else 0,
            'Memory_Usage': float(record['Median_Speed']) if record['Median_Speed'] is not None else 0,
            'Network_Usage': float(record['Top_Speed']) if record['Top_Speed'] is not None else 0,
            'Disk_Usage': float(record['Low_Speed']) if record['Low_Speed'] is not None else 0
        })

    return jsonify(formatted_data), 200


#Get the available dates from the system
@performance.route('/performance/dates', methods=['GET'])
def get_available_dates():
    try:
        cursor = db.get_db().cursor()
        cursor.execute('SELECT DISTINCT Date FROM Performance ORDER BY Date DESC')
        dates = cursor.fetchall()
        cursor.close()
        
        # Format dates as YYYY-MM-DD strings
        date_list = []
        for date_record in dates:
            if isinstance(date_record, dict):
                date_str = date_record['Date']
            else:
                date_str = date_record[0]
                
            # Parse the date string and reformat it
            date_obj = datetime.strptime(str(date_str), '%Y-%m-%d %H:%M:%S')
            formatted_date = date_obj.strftime('%Y-%m-%d')
            date_list.append(formatted_date)
            
        return jsonify(date_list), 200
        
    except Exception as e:
        print(f"Error in get_available_dates: {str(e)}")  # Debug print
        return jsonify({'error': str(e)}), 500
    