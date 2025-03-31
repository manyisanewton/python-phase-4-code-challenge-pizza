#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# Resource for /restaurants
class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [Restaurant.to_dict() for Restaurant in restaurants], 200

# Resource for /restaurants/<int:id>
class RestaurantById(Resource):
    def get(self, id):
        Restaurant = Restaurant.query.get(id)
        if not Restaurant:
            return {"error": "Restaurant not found"}, 404
        # Include restaurant_pizzas in the response
        return Restaurant.to_dict(rules=('restaurant_pizzas',)), 200

    def delete(self, id):
        Restaurant = Restaurant.query.get(id)
        if not Restaurant:
            return {"error": "Restaurant not found"}, 404
        db.session.delete(Restaurant)
        db.session.commit()
        return '', 204

# Resource for /pizzas
class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict() for pizza in pizzas], 200

# Resource for /restaurant_pizzas
class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            # Validation for the required fields
            if not all(key in data for key in ['price', 'pizza_id', 'restaurant_id']):
                return {"errors": ["validation errors"]}, 400

            # Checking if Pizza and Restaurant  are existing 
            pizza = Pizza.query.get(data['pizza_id'])
            Restaurant = Restaurant.query.get(data['restaurant_id'])
            if not pizza or not Restaurant:
                return {"errors": ["validation errors"]}, 400

            # creating a new Restaurant
            restaurant_pizza = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            
            
            db.session.add(restaurant_pizza)
            db.session.commit()
            return restaurant_pizza.to_dict(), 201

        except ValueError as e:
            return {"errors": ["validation errors"]}, 400

# api resources
api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantById, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)