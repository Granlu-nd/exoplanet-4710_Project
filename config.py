import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'secret-key'  # you can randomize this
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'exoplanets.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
