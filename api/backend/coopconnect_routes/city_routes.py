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

