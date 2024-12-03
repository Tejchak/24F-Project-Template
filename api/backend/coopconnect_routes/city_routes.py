from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db


#returns a list of all cities
cities = Blueprint('City', __name__)

@cities.route('/cities', methods=['GET'])
def get_all_cities():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM City")
        cities_data = cursor.fetchall()
        cursor.close()

        cities_list = []
        for city in cities_data:
            cities_list.append({
                'city_id': city[0],
                'avg_cost_of_living': city[1],
                'avg_rent': city[2],
                'avg_wage': city[3],
                'name': city[4],
                'population': city[5],
                'prop_hybrid_workers': float(city[6]) if city[6] else None
            })

        return jsonify(cities_list), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#returns the details of a specific city
@cities.route('/cities/<city_name>', methods=['GET'])
def get_city_details(city_name):
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT City_ID, Avg_Cost_Of_Living, Avg_Rent, Avg_Wage, 
                   Name, Population, Prop_Hybrid_Workers 
            FROM City 
            WHERE Name = %s
        """, (city_name,))
        city_data = cursor.fetchall()
        cursor.close()

        if not city_data:
            return jsonify({'error': 'City not found'}), 404

        city_details = {
            'city_id': city_data[0],
            'avg_cost_of_living': city_data[1],
            'avg_rent': city_data[2],
            'avg_wage': city_data[3],
            'name': city_data[4],
            'population': city_data[5],
            'prop_hybrid_workers': float(city_data[6]) if city_data[6] else None
        }

        return jsonify(city_details), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


