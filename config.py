import os
from datetime import timedelta

# General config
SECRET_KEY = 'your-secret-key-here'  # Change this to a random secure string in production
SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Session config
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# Directory paths
STATIC_FOLDER = 'static'
TEMPLATE_FOLDER = 'templates'