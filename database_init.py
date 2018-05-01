from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Instrument, User, database_info
from sqlalchemy.engine.url import URL

engine = create_engine(URL(**database_info))
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

categories = {"Strings", "Woodwinds", "Brass", "Percussion", "Keyboard"}
for category_name in categories:
    session.add(Category(name=category_name))
    session.commit()
