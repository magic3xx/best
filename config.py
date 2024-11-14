import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'magic-trading-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///licenses.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False