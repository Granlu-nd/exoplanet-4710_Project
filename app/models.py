from . import db

class Missions(db.Model):
    mission_id = db.Column(db.Integer, primary_key=True) # Mission id – Primary key (Integer)
    name = db.Column(db.String(100), nullable=False) # Name – name of the mission 
    num_planets_found = db.Column(db.Integer, nullable=False) # Number of planets found – number of planets found by the mission (Integer)
    launch_year = db.Column(db.Integer, nullable=False) # Launch Year – Yeah of launch (Integer)
    agency = db.Column(db.String(100), nullable=False) # Agency – name of the agency (String)

    planets = db.relationship('Planet', backref='mission', lazy=True)

class StarSystem(db.Model):
    system_id = db.Column(db.Integer, primary_key=True) # System id – Primary key (Integer)
    name = db.Column(db.String(100)) # Name – name of the star system (String)
    distance_from_earth = db.Column(db.Float)  # Distance from Earth – distance from Earth in light years (Float)
    galaxy = db.Column(db.String(100)) # Galaxy – name of the galaxy (String)
    discovery_year = db.Column(db.Integer) # Discovery Year – year of discovery (Integer)

    stars = db.relationship('Star', backref='system', lazy=True) # Relationship to Star model

class Star(db.Model):
    star_id = db.Column(db.Integer, primary_key=True) # Star id – Primary key (Integer)
    name = db.Column(db.String(100)) # Name – name of the star (String)
    spectral_type = db.Column(db.String(20)) # Spectral Type – Classification based on its temperature (String)
    temperature = db.Column(db.Float) # Temperature – surface temperature in Kelvin (Float)
    mass = db.Column(db.Float) # Mass – mass in solar masses (Float)
    luminosity = db.Column(db.Float) # Luminosity – luminosity in solar luminosities (Float)
    age = db.Column(db.Float) # Age – age in billions of years (Float)

    system_id = db.Column(db.Integer, db.ForeignKey('star_system.system_id')) # Foreign key linking to a star_system -> Each star belongs to one system.
    planets = db.relationship('Planet', backref='star', lazy=True) # Relationship to Planet model

class Planet(db.Model):
    planet_id = db.Column(db.Integer, primary_key=True) # Planet id – Primary key (Integer)
    name = db.Column(db.String(100)) # Name – name of the planet (String)
    mass = db.Column(db.Float) # Mass – mass in kilograms (Float)
    radius = db.Column(db.Float) # Radius – radius in kilometers (Float)
    distance_from_star = db.Column(db.Float) # Distance from Star – distance from the star in astronomical units (Float)
    orbital_period = db.Column(db.Float) # Orbital Period – time taken to complete one orbit in Earth days (Float)
    rotational_period = db.Column(db.Float) # Rotational Period – time taken to complete one rotation in Earth hours (Float)
    atmosphere_composition = db.Column(db.String(255)) # Atmosphere Composition – composition of the atmosphere (String)
    surface_temperature = db.Column(db.Float) # Surface Temperature – temperature in Celsius (Float)

    star_id = db.Column(db.Integer, db.ForeignKey('star.star_id')) # Foreign key linking to a star -> Each planet belongs to one star.
    mission_id = db.Column(db.Integer, db.ForeignKey('missions.mission_id')) # Foreign key linking to a mission -> Each planet can be linked to one mission.

    habitability = db.relationship('Habitability', backref='planet', uselist=False) # Relationship to Habitability model

class Habitability(db.Model):
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.planet_id'), primary_key=True) # Foreign key linking to a planet -> Each habitability record is linked to one planet.
    water_presence = db.Column(db.Boolean) # Water Presence – presence of water (Boolean)
    radiation_exposure = db.Column(db.Float) # Radiation Exposure – radiation exposure in sieverts (Float)
    atmosphere_pressure = db.Column(db.Float) # Atmosphere Pressure – pressure in pascals (Float)
    gravity = db.Column(db.Float) # Gravity – gravity in m/s² (Float)
    habitability_score = db.Column(db.Float) # Habitability Score – score based on various factors (Float)

#For user Role Creation 

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True) # User id – Primary key (Integer)
    username = db.Column(db.String(50), unique=True, nullable=False) # Username – unique username (String)
    email = db.Column(db.String(100), unique=True, nullable=False) # Email – unique email address (String)
    role = db.Column(db.String(20), nullable=False)  # store "student" or "researcher"
    
    studying = db.relationship('UserPlanet', backref='user', lazy=True) # Relationship to UserPlanet table

class UserPlanet(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Primary key (Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False) # Foreign key linking to a user (Integer)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.planet_id'), nullable=False) # Foreign key linking to a planet (Integer)

    nickname = db.Column(db.String(100)) # Nickname – nickname for the planet (String)
    favorite = db.Column(db.Boolean, default=False) # Favorite – whether the planet is marked as favorite (Boolean)
    notes = db.Column(db.Text) # Notes – user notes about the planet (Text)

    planet = db.relationship('Planet', backref='studied_by', lazy=True) 

