from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists
from sqlalchemy import create_engine
import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)

Base = declarative_base()

#Create the database if it does not exists:
if not database_exists(engine.url):
    from models import *
    Base.metadata.create_all(engine)

# Create a database session
Session = sessionmaker()
Session.configure(bind=engine)

db = Session()