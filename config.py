import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'bc9b2d89c5fbfd81232bac5cde78897f')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///purchase_sales.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False