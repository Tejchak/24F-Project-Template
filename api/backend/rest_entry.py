from flask import Flask

from backend.db_connection import db
from backend.customers.customer_routes import customers
from backend.products.products_routes import products
from backend.simple.simple_routes import simple_routes
from backend.coopconnect_routes.city_routes import cities
from backend.coopconnect_routes.performance_routes import performance
from backend.coopconnect_routes.user_routes import users
from backend.coopconnect_routes.employer import employer
from backend.coopconnect_routes.housing_routes import housing
from backend.coopconnect_routes.airport_routes import airports
from backend.coopconnect_routes.hospital_routes import hospitals
from backend.coopconnect_routes.student_route import student
from backend.coopconnect_routes.location_routes import locations
from backend.coopconnect_routes.job_routes import job_routes
import os
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)

    # Load environment variables
    # This function reads all the values from inside
    # the .env file (in the parent folder) so they
    # are available in this file.  See the MySQL setup 
    # commands below to see how they're being used.
    load_dotenv()

    # secret key that will be used for securely signing the session 
    # cookie and can be used for any other security related needs by 
    # extensions or your application
    # app.config['SECRET_KEY'] = 'someCrazyS3cR3T!Key.!'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # # these are for the DB object to be able to connect to MySQL. 
    # app.config['MYSQL_DATABASE_USER'] = 'root'
    app.config['MYSQL_DATABASE_USER'] = os.getenv('DB_USER').strip()
    app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_ROOT_PASSWORD').strip()
    app.config['MYSQL_DATABASE_HOST'] = os.getenv('DB_HOST').strip()
    app.config['MYSQL_DATABASE_PORT'] = int(os.getenv('DB_PORT').strip())
    app.config['MYSQL_DATABASE_DB'] = 'coopConnect'  # Change this to your DB name

    # Initialize the database object with the settings above. 
    app.logger.info('current_app(): starting the database connection')
    db.init_app(app)


    # Register the routes from each Blueprint with the app object
    # and give a url prefix to each
    app.logger.info('current_app(): registering blueprints with Flask app object.')   
    app.register_blueprint(simple_routes)
    app.register_blueprint(customers,   url_prefix='/c')
    app.register_blueprint(products,    url_prefix='/p')
    app.register_blueprint(cities)
    app.register_blueprint(performance)
    app.register_blueprint(users)
    app.register_blueprint(employer)
    app.register_blueprint(housing)
    app.register_blueprint(airports)
    app.register_blueprint(hospitals)
    app.register_blueprint(student, url_prefix='/students')
    app.register_blueprint(locations)
    app.register_blueprint(job_routes)
    # Don't forget to return the app object
    return app

