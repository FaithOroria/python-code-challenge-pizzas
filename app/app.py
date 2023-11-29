#!/usr/bin/env python3

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pizza.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    @app.route('/restaurants', methods=['GET'])
    def fetch_restaurants():
        restaurants = Restaurant.query.all()
        return jsonify([{'id': r.id, 'name': r.name, 'address': r.address} for r in restaurants])

    @app.route('/restaurants/<int:restaurant_id>', methods=['GET'])
    def fetch_single_restaurant(restaurant_id):
        restaurant = Restaurant.query.get(restaurant_id)

        if restaurant is None:
            return jsonify({'error': 'Sorry, the restaurant could not be found.'}), 404

        pizzas = [{'id': rp.pizza.id, 'name': rp.pizza.name, 'ingredients': rp.pizza.ingredients, 'price': rp.price} for rp in restaurant.restaurant_pizzas]

        return jsonify({
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'pizzas': pizzas
        })

    @app.route('/pizzas', methods=['GET'])
    def fetch_pizzas():
        pizzas = Pizza.query.all()
        return jsonify([{'id': p.id, 'name': p.name, 'ingredients': p.ingredients} for p in pizzas])

    @app.route('/restaurant_pizzas', methods=['POST'])
    def add_restaurant_pizza():
        data = request.get_json()
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        if not (price and pizza_id and restaurant_id):
            return jsonify({'errors': ['Validation failed. Please check your input.']}), 400

        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)

        db.session.add(restaurant_pizza)
        db.session.commit()

        pizza = Pizza.query.get(pizza_id)

        return jsonify({
            'id': pizza.id,
            'name': pizza.name,
            'ingredients': pizza.ingredients,
            'price': restaurant_pizza.price
        }), 201

    @app.route('/restaurants/<int:id>', methods=['DELETE'])
    def delete_restaurant(id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404
        
       
        RestaurantPizza.query.filter_by(restaurant_id=id).delete()

        
        db.session.delete(restaurant)
        db.session.commit()

        return '', 204 

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5555)
