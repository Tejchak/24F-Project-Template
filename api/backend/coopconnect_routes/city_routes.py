from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db


#returns a list of all cities
cities = Blueprint('city', __name__)

@cities.route('/city', methods=['GET'])
def get_all_cities():
    try:
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM City")
        cities_data = cursor.fetchall()
        cursor.close()

        cities_list = []
        for city in cities_data:
            cities_list.append({
                'city_id': city['City_ID'],
                'avg_cost_of_living': city['Avg_Cost_Of_Living'],
                'avg_rent': city['Avg_Rent'],
                'avg_wage': city['Avg_Wage'],
                'name': city['Name'],
                'population': city['Population'],
                'prop_hybrid_workers': float(city['Prop_Hybrid_Workers']) if city['Prop_Hybrid_Workers'] else None
            })

        return jsonify(cities_list), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#returns the cost analysis of a specific city
@cities.route('/city/<CityID>/<Avg_Cost_Of_Living>', methods=['GET'])
def get_city_cost_analysis(CityID, Avg_Cost_Of_Living):
    try:
        cursor = db.get_db().cursor()
        target_cost = int(Avg_Cost_Of_Living)
        
        margin = target_cost * 0.2  # Increased to 40% range for more results
        min_cost = target_cost - margin
        max_cost = target_cost + margin
        
        query = """
            SELECT c1.Name, 
                    c1.Avg_Cost_Of_Living,
                    c1.Avg_Rent,
                    c1.Avg_Wage,
                    c1.Avg_Cost_Of_Living / c1.Avg_Wage as cost_to_wage_ratio,
                    c1.Avg_Rent / c1.Avg_Wage as rent_to_wage_ratio,
                    (SELECT AVG(Avg_Cost_Of_Living) FROM City) as avg_national_col,
                    (SELECT AVG(Avg_Rent) FROM City) as avg_national_rent,
                    (SELECT AVG(Avg_Wage) FROM City) as avg_national_wage
            FROM City c1
            WHERE c1.Avg_Cost_Of_Living BETWEEN %s AND %s
            ORDER BY ABS(c1.Avg_Cost_Of_Living - %s)
            LIMIT 5
        """
        
        cursor.execute(query, (min_cost, max_cost, target_cost))
        cities_data = cursor.fetchall()
        cursor.close()

        if not cities_data:
            return jsonify({'error': 'No cities found matching the specified cost of living'}), 404

        cities_analysis = []
        for city_data in cities_data:
            cost_analysis = {
                'name': city_data['Name'],
                'cost_of_living': float(city_data['Avg_Cost_Of_Living']),
                'avg_rent': float(city_data['Avg_Rent']),
                'avg_wage': float(city_data['Avg_Wage']),
                'cost_metrics': {
                    'cost_to_wage_ratio': float(city_data['cost_to_wage_ratio']),
                    'rent_to_wage_ratio': float(city_data['rent_to_wage_ratio']),
                    'cost_vs_national_avg': {
                        'cost_of_living_percent': (city_data['Avg_Cost_Of_Living'] / city_data['avg_national_col'] * 100) - 100,
                        'rent_percent': (city_data['Avg_Rent'] / city_data['avg_national_rent'] * 100) - 100,
                        'wage_percent': (city_data['Avg_Wage'] / city_data['avg_national_wage'] * 100) - 100
                    }
                }
            }
            cities_analysis.append(cost_analysis)

        return jsonify(cities_analysis), 200

    except Exception as e:
        print(f"Error in get_city_cost_analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500


