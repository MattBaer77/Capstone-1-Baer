"""Seed database with sample data and data from API."""

from csv import DictReader
from app import db
from models import User, Message, Follows


db.drop_all()
db.create_all()

