from flask import render_template, request
from . import db
from .models import Planet, Missions
from flask import Blueprint
from sqlalchemy.orm import joinedload  # 👈 Needed for eager loading

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/planets')
def planets():
    name_query = request.args.get('name')
    min_temp = request.args.get('min_temp', type=float)
    max_temp = request.args.get('max_temp', type=float)
    min_radius = request.args.get('min_radius', type=float)
    max_radius = request.args.get('max_radius', type=float)
    mission_query = request.args.get('mission')
    
    query = Planet.query.options(
        joinedload(Planet.star),
        joinedload(Planet.mission)
    )

    # filters
    if name_query:
        query = query.filter(Planet.name.ilike(f"%{name_query}%"))
    if min_temp is not None:
        query = query.filter(Planet.surface_temperature >= min_temp)
    if max_temp is not None:
        query = query.filter(Planet.surface_temperature <= max_temp)
    if min_radius is not None:
        query = query.filter(Planet.radius >= min_radius)
    if max_radius is not None:
        query = query.filter(Planet.radius <= max_radius)
    if mission_query:
        query = query.join(Planet.mission).filter(Missions.name.ilike(f"%{mission_query}%"))

    planets = query.limit(200).all()

    return render_template('planets.html', planets=planets)
