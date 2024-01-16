#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return ''

#Creates the route for returning all scientists, or posting a new scientist.
class Scientists_Route(Resource):
    def get(self):
        all_scientists = Scientist.query.all()
        scientist_dict = []
        for scientist in all_scientists:
            scientist_dict.append(scientist.to_dict(rules = ('-missions',)))
        return make_response(scientist_dict, 200)
    def post(self):
        try:
            data = request.get_json()
            new_scientist = Scientist(
                name= data["name"],
                field_of_study= data["field_of_study"],
            )
            if new_scientist:
                db.session.add(new_scientist)
                db.session.commit()
                return make_response(new_scientist.to_dict(rules= ('-missions',)), 201)
        except:
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(Scientists_Route, '/scientists')

#Creates the route for a single scientist via an ID, including a GET, PATCH, and DELETE request
class Scientists_By_Id(Resource):
    def get(self, id):
        one_scientist = Scientist.query.filter(Scientist.id == id).first()
        if one_scientist:
            return make_response(one_scientist.to_dict(), 200)
        else:
            return make_response({"error": "Scientist not found"}, 404)
    def patch(self, id):
        one_scientist = Scientist.query.filter(Scientist.id == id).first()
        if one_scientist:
            try:
                data = request.get_json()
                for attr in data:
                    setattr(one_scientist, attr, data[attr])
                db.session.add(one_scientist)
                db.session.commit()
                return make_response(one_scientist.to_dict(rules = ('-missions',)), 202)
            except:
                return make_response({"errors": ["validation errors"]}, 400)
        else:
            return make_response({"error": "Scientist not found"}, 404)
    def delete(self, id):
        one_scientist = Scientist.query.filter(Scientist.id == id).first()
        if one_scientist:
            db.session.delete(one_scientist)
            db.session.commit()
            return make_response({}, 204)
        else:
            return make_response({"error": "Scientist not found"}, 404)

api.add_resource(Scientists_By_Id, '/scientists/<int:id>')

#Creates the route for all planets via a GET request
class Planets_Route(Resource):
    def get(self):
        all_planets = Planet.query.all()
        planets_dict = []
        for planet in all_planets:
            planets_dict.append(planet.to_dict(rules = ('-missions',)))
        return make_response(planets_dict, 200)

api.add_resource(Planets_Route, '/planets')

#Creates a route for POSTing a new mission
class Mission_Route(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_mission = Mission(
                name= data["name"],
                scientist_id= data["scientist_id"],
                planet_id= data["planet_id"],
            )
            if new_mission:
                db.session.add(new_mission)
                db.session.commit()
                return make_response(new_mission.to_dict(), 201)
        except:
            return make_response({"errors": ["validation errors"]}, 400)
        
            

api.add_resource(Mission_Route, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
