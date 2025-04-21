from flask import render_template, request, flash, redirect, url_for
from . import db
from .models import Planet, Star, Missions, User, UserPlanet
from flask import Blueprint
from sqlalchemy.orm import joinedload 

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
    planets = Planet.query.order_by(Planet.name).limit(200).all()
    return render_template('profile.html', user=user, planets=planets)

@main.route('/users')
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@main.route('/profile/<username>/add_planet', methods=['POST'])
def add_planet(username):
    user = User.query.filter_by(username=username).first_or_404()

    planet_id = request.form.get('planet_id')
    nickname = request.form.get('nickname')
    favorite = bool(request.form.get('favorite'))
    notes = request.form.get('notes')

    # prevent duplicates
    existing = UserPlanet.query.filter_by(user_id=user.user_id, planet_id=planet_id).first()
    if existing:
        flash('Planet already added.')
        return redirect(url_for('main.profile', username=username))

    studying = UserPlanet(
        user_id=user.user_id,
        planet_id=planet_id,
        nickname=nickname,
        favorite=favorite,
        notes=notes
    )
    db.session.add(studying)
    db.session.commit()
    flash('Planet added to your study list!')
    return redirect(url_for('main.profile', username=username))

@main.route('/remove_study/<int:study_id>', methods=['POST'])
def remove_study(study_id):
    study = UserPlanet.query.get_or_404(study_id)
    username = study.user.username
    db.session.delete(study)
    db.session.commit()
    flash("Planet removed from study list.")
    return redirect(url_for('main.profile', username=study.user.username))

@main.route('/edit_study/<int:study_id>', methods=['GET', 'POST'])
def edit_study(study_id):
    study = UserPlanet.query.get_or_404(study_id)

    if request.method == 'POST':
        study.nickname = request.form.get('nickname')
        study.notes = request.form.get('notes')
        study.favorite = bool(request.form.get('favorite'))
        db.session.commit()
        flash("Study details updated!")
        return redirect(url_for('main.profile', username=study.user.username))

    return render_template('edit_study.html', study=study)

@main.route('/delete-user/<username>', methods=['GET', 'POST'])
def confirm_delete_user(username):
    user = User.query.filter_by(username=username).first_or_404()

    if request.method == 'POST':
        # Delete all planet study relationships
        UserPlanet.query.filter_by(user_id=user.user_id).delete()

        # Then delete the user
        db.session.delete(user)
        db.session.commit()

        flash(f"User '{username}' deleted.")
        return redirect(url_for('main.home'))

    return render_template('confirm_delete.html', user=user)

# SQL Demo Route
# This route is for demonstration purposes.
@main.route('/sql-demo')
def sql_demo():
    from sqlalchemy import func

    # 1. Top 10 missions by number of planets
    mission_counts = (
        db.session.query(Missions.name, func.count(Planet.planet_id).label('planet_count'))
        .join(Planet)
        .group_by(Missions.name)
        .order_by(func.count(Planet.planet_id).desc())
        .limit(10)
        .all()
    )

    # 2. Average surface temp by star
    avg_temps = (
        db.session.query(Star.name, func.avg(Planet.surface_temperature).label('avg_temp'))
        .join(Planet)
        .group_by(Star.name)
        .order_by(func.avg(Planet.surface_temperature).desc())
        .limit(10)
        .all()
    )

    # 3. Planets discovered by year
    planets_by_year = (
        db.session.query(Missions.launch_year, func.count(Planet.planet_id))
        .join(Planet)
        .group_by(Missions.launch_year)
        .order_by(Missions.launch_year)
        .all()
    )

    return render_template(
        'sql_demo.html',
        mission_counts=mission_counts,
        avg_temps=avg_temps,
        planets_by_year=planets_by_year
    )

@main.route('/habitability-hub')
def habitability_hub():
    return render_template('habitability_hub.html')
