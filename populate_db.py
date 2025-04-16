import pandas as pd
from app import create_app, db
from app.models import Planet, Star, Missions

# Helper to safely convert values to float
def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

# Load cleaned dataset
df = pd.read_csv("data/exoplanets_3.csv", skiprows=98)

# Keep only relevant columns
df = df[[
    'pl_name', 'pl_bmasse', 'pl_rade', 'pl_orbsmax', 'pl_orbper', 'pl_eqt',
    'hostname', 'st_teff', 'st_mass',
    'discoverymethod', 'disc_year', 'disc_facility', 'sy_dist'
]]

# Create app context
app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()

    for _, row in df.iterrows():
        try:
            # Skip rows without required fields
            if pd.isnull(row['pl_name']) or pd.isnull(row['hostname']):
                raise ValueError("Missing planet or star name.")

            # Mission setup
            agency = row['disc_facility']
            if pd.isnull(agency) or str(agency).strip() == "":
                raise ValueError("Missing mission agency.")

            year = int(row['disc_year']) if not pd.isnull(row['disc_year']) else 0

            mission = Missions.query.filter_by(agency=agency).first()
            if not mission:
                mission = Missions(
                    name=agency,
                    num_planets_found=0,
                    launch_year=year,
                    agency=agency
                )
                db.session.add(mission)
                db.session.flush()

            # Star setup
            star = Star(
                name=row['hostname'],
                spectral_type=row.get('discoverymethod', 'Unknown'),
                temperature=safe_float(row.get('st_teff')),
                mass=safe_float(row.get('st_mass')),
                luminosity=None,
                age=None,
                system_id=None
            )
            db.session.add(star)
            db.session.flush()

            # Planet setup
            planet = Planet(
                name=row['pl_name'],
                mass=safe_float(row.get('pl_bmasse')),
                radius=safe_float(row.get('pl_rade')),
                distance_from_star=safe_float(row.get('pl_orbsmax')),
                orbital_period=safe_float(row.get('pl_orbper')),
                rotational_period=None,
                atmosphere_composition=None,
                surface_temperature=safe_float(row.get('pl_eqt')),
                star_id=star.star_id,
                mission_id=mission.mission_id
            )
            db.session.add(planet)
            mission.num_planets_found += 1

        except Exception as e:
            db.session.rollback()
            print(f"⚠️ Error with planet {row.get('pl_name')}: {e}")
            continue

    db.session.commit()
    print("✅ Database successfully populated with cleaned NASA dataset!")
