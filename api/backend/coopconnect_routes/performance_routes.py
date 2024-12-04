from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db


#Creates a new blueprint to collect the routes
performance = Blueprint('Performance', __name__)



#Get all performance info from the system on a given day
@performance.route('/performance/<Date>', methods=['GET'])
def get_performance(Date):
    cursor = db.get_db().cursor()
    cursor.execute('SELECT * FROM Performance WHERE Date = %s', (Date,))
    performance_data = cursor.fetchall()
    cursor.close()

    # Convert the data to a list of dictionaries
    formatted_data = []
    for record in performance_data:
        formatted_data.append({
            'PID': record[0],
            'CPU_Usage': float(record[1]) if record[1] else 0,
            'Memory_Usage': float(record[2]) if record[2] else 0,
            'Network_Usage': float(record[3]) if record[3] else 0,
            'Disk_Usage': float(record[4]) if record[4] else 0
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
            date_obj = date_record[0]
            formatted_date = date_obj.strftime('%Y-%m-%d')
            date_list.append(formatted_date)
            
        return jsonify(date_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500