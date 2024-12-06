from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from datetime import datetime
from backend.db_connection import db

system_admin = Blueprint('system_admin_routes', __name__)

#Get all performance info from the system on a given day
@system_admin.route('/performance/<Date>', methods=['GET'])
def get_performance(Date):
    cursor = db.get_db().cursor()
    cursor.execute('SELECT * FROM Performance WHERE date(`Date`) = %s', (Date,))
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
            'Disk_Usage': float(record['Low_Speed']) if record['Low_Speed'] is not None else 0,
            'Date': record['Date']
        })

    return jsonify(formatted_data), 200


#Get the available dates from the system
@system_admin.route('/performance/dates', methods=['GET'])
def get_available_dates():
    try:
        cursor = db.get_db().cursor()
        cursor.execute('''SELECT DISTINCT `Date` FROM Performance ORDER BY `Date` DESC''')
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
    

# Add new performance entry
@system_admin.route('/performance/add', methods=['POST'])
def add_performance():
    try:
        data = request.json
        cursor = db.get_db().cursor()
        
        query = '''
        INSERT INTO Performance (`Date`, Avg_Speed, Median_Speed, Top_Speed, Low_Speed)
        VALUES (%s, %s, %s, %s, %s)
        '''
        
        cursor.execute(query, (
            data['date'],
            data['cpu_usage'],
            data['memory_usage'],
            data['network_usage'],
            data['disk_usage']
        ))
        
        db.get_db().commit()
        cursor.close()
        return jsonify({"message": "Performance entry added successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update existing performance entry
@system_admin.route('/performance/update/<date>', methods=['PUT'])
def update_performance(date):
    try:
        data = request.json
        cursor = db.get_db().cursor()
        
        query = '''
        UPDATE Performance 
        SET Avg_Speed = %s, 
            Median_Speed = %s, 
            Top_Speed = %s, 
            Low_Speed = %s
        WHERE date(`Date`) = %s
        '''
        
        cursor.execute(query, (
            data['cpu_usage'],
            data['memory_usage'],
            data['network_usage'],
            data['disk_usage'],
            date
        ))
        
        db.get_db().commit()
        cursor.close()
        return jsonify({"message": "Performance entry updated successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete performance entry
@system_admin.route('/performance/delete/<date>', methods=['DELETE'])
def delete_performance(date):
    try:
        cursor = db.get_db().cursor()
        query = 'DELETE FROM Performance WHERE date(`Date`) = %s'
        cursor.execute(query, (date,))
        
        db.get_db().commit()
        cursor.close()
        return jsonify({"message": "Performance entry deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Return a list of all users with their respective information
@system_admin.route('/user', methods=['GET'])
def get_users():

    cursor = db.get_db().cursor()
    cursor.execute('SELECT * FROM User JOIN Category ON User.CategoryID = Category.CategoryID')
                   
    
    theData = cursor.fetchall()
    
    the_response = make_response(jsonify(theData))
    the_response.status_code = 200
    return the_response