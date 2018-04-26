from sqlalchemy import create_engine
from database_setup import Base, Category, Instrument, User, database_info
from sqlalchemy.engine.url import URL

engine = create_engine(URL(**database_info))

Base.metadata.bind = engine
Base.metadata.drop_all(engine)
