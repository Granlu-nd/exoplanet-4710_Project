from flask import render_template, request, flash, redirect, url_for
from . import db
from .models import Planet, Missions, User
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

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists.')
            return redirect(url_for('main.register'))

        new_user = User(username=username, email=email, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash('User profile created successfully!')
        return redirect(url_for('main.home'))

    return render_template('register.html')

@main.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)

@main.route('/users')
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)
