import sys
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'user_table'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    instrument = relationship("Instrument",
                              cascade="all, delete-orphan",
                              backref="user_table")

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }


class Category(Base):
    __tablename__ = 'category'
    name = Column(String(80), primary_key=True)
    instrument = relationship("Instrument",
                              cascade="all, delete-orphan",
                              backref="category")

    @property
    def serialize(self):
        return {
            'name': self.name
        }


class Instrument(Base):
    __tablename__ = 'instrument'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    category_name = Column(String(80), ForeignKey('category.name'))
    user_id = Column(Integer, ForeignKey('user_table.id'))
    __table_args__ = (UniqueConstraint(
                            'category_name', 'name', name='category_name_uc'),)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category_name
        }


database_info = {
    'drivername': 'postgresql',
    'host': 'localhost',
    'port': '5432',
    'username': 'vagrant',
    'password': 'vagrant',
    'database': 'vagrant',
}

engine = create_engine(URL(**database_info))

Base.metadata.create_all(engine)
