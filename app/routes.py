from flask import render_template, request, flash, redirect, url_for
from . import db
from .models import Planet, Star, Missions, User, UserPlanet
from flask import Blueprint
from sqlalchemy.orm import joinedload
from sqlalchemy import func 

main = Blueprint('main', __name__)

@main.route('/') #done
def home():
    return render_template('home.html')

@main.route('/planets') #done
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

@main.route('/register', methods=['GET', 'POST']) #done
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

@main.route('/profile/<username>') #done
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    planets = Planet.query.order_by(Planet.name).limit(200).all()

    planet_count = ( # count of planets associated with the user
    db.session.query(func.count(UserPlanet.planet_id))
    .filter_by(user_id=user.user_id)
    .scalar()
    )

    return render_template('profile.html', user=user, planets=planets, planet_count=planet_count)

@main.route('/users') #done
def users():
    all_users = User.query.all() # SELECT * FROM user;
    return render_template('users.html', users=all_users)

@main.route('/profile/<username>/add_planet', methods=['POST']) #done
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

@main.route('/remove_study/<int:study_id>', methods=['POST']) #done
def remove_study(study_id):
    study = UserPlanet.query.get_or_404(study_id)
    username = study.user.username
    db.session.delete(study)
    db.session.commit()
    flash("Planet removed from study list.")
    return redirect(url_for('main.profile', username=study.user.username))

@main.route('/edit_study/<int:study_id>', methods=['GET', 'POST']) #done
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

@main.route('/delete-user/<username>', methods=['GET', 'POST']) #done
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
@main.route('/sql-demo') #done
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


#Advanced Feature: Habitability Fucntions 
#Route to display habitability Hub page
@main.route('/habitability-hub') #done
def habitability_hub():
    return render_template('habitability_hub.html')
#Route to display "What if Earth was there?" simulation page
@main.route('/habitability-sim', methods=['GET', 'POST']) #done
def habitability_sim():
    planets = Planet.query.limit(200).all()
    result = None
    radiation_warning = None
    warnings = []
    planet_data = {}

    if request.method == 'POST':
        selected_id = request.form.get('planet_id')
        planet = (
            db.session.query(Planet)
            .options(joinedload(Planet.star)) 
            .filter_by(planet_id=int(selected_id))
            .first()
        )

        # Try to use real data
        name = planet.name
        radius = planet.radius
        temp = planet.surface_temperature

        # Check if we’re missing data
        if not radius or not temp:
            warnings.append("Missing data detected. Please input estimated values or use random Earth-like values.")

        # Grab custom input if user filled it out
        custom_radius = request.form.get('custom_radius')
        custom_temp = request.form.get('custom_temp')

        # Use overrides or fill with Earth-like defaults
        try:
            radius = float(custom_radius) if custom_radius else (radius if radius else 1.0)
            temp = float(custom_temp) if custom_temp else (temp if temp else 15.0)
        except ValueError:
            warnings.append("Invalid custom values. Using default values.")

        # Simulate result
        if temp > 100 or temp < -50:
            result = f"🔥 Earth would likely not survive. Temperature is {temp}°C — extreme and dangerous."
        elif radius > 5:
            result = f"🌍 Earth might survive the temp ({temp}°C), but gravity from radius {radius} Earths would crush human structures."
        else:
            result = f"✅ Earth could survive. Temp is {temp}°C and radius {radius}x Earth — within survivable ranges."

        radiation_warning = ""
        if planet.star and planet.star.temperature:
            if planet.star.temperature > 4700:
                radiation_warning = f"☢️ Warning: The host star is extremely hot ({planet.star.temperature} K), suggesting high radiation levels. Earth would need shielding."


        planet_data = {
            'name': name,
            'radius': radius,
            'temp': temp,
            'star': planet.star.name if planet.star else "Unknown"
        }

    return render_template("habitability_sim.html", planets=planets, result=result, planet_data=planet_data, warnings=warnings, radiation_warning =radiation_warning)
#Route to display "Danger Index" info page
@main.route('/danger-index') #done
def danger_index():
    from sqlalchemy import func

    # JOIN Planet and Star to get star temperature
    danger_data = (
        db.session.query(
            Planet.name,
            Planet.surface_temperature,
            Planet.radius,
            Planet.mass,
            Star.temperature.label('star_temp')
        )
        .join(Star, Planet.star_id == Star.star_id, isouter=True)
        .limit(500)
        .all()
    )

    categorized = {4: [], 3: [], 2: [], 1: [], 0: []}

    def calculate_danger(p):
        score = 0
        notes = []

        # Surface Temp
        if p.surface_temperature is None:
            score += 1
            notes.append("Missing temp")
        elif p.surface_temperature > 60 or p.surface_temperature < -50:
            score += 2
            notes.append("Extreme surface temp")

        # Radius
        if p.radius is None:
            score += 1
            notes.append("Missing radius")
        elif p.radius < 0.5 or p.radius > 3:
            score += 1
            notes.append("Unfavorable radius")

        # Mass
        if p.mass is None:
            score += 1
            notes.append("Missing mass")
        elif p.mass > 10:
            score += 1
            notes.append("Very high mass")

        if p.star_temp is None:
            score += 1
            notes.append("Unknown radiation")
        elif p.star_temp > 7100:
            score += 1
            notes.append("VERY High radiation from hot star")
        elif p.star_temp > 6500:
            score += 1
            notes.append("High radiation from hot star")
        elif p.star_temp < 3700:
            notes.append("Very cool star (dim) — possible light/energy challenges")

        return min(score, 4), ", ".join(notes)

    for p in danger_data:
        score, reasons = calculate_danger(p)
        categorized[score].append({
            'name': p.name,
            'score': score,
            'notes': reasons
        })

    return render_template('danger_index.html', categorized=categorized)


