from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Instrument, User, database_info
from sqlalchemy.engine.url import URL

engine = create_engine(URL(**database_info))
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# categories = {"Strings", "Woodwinds", "Brass", "Percussion", "Keyboard"}
# for category_name in categories:
#     session.add(Category(name=category_name))
#     session.commit()
#
# session.add(User(name="titus",
#                  email="titusc711@gmail.com"))
# session.commit()
#
# session.add(User(name="t3tra",
#                  email="tmchen@berkeley.edu"))
# session.commit()
#
# session.add(Instrument(name="Piano",
#                        description="It's a piano.",
#                        category_name="Keyboard",
#                        user_id=1))
# session.commit()
#
# session.add(Instrument(name="Violin",
#                        description="It's a violin.",
#                        category_name="Strings",
#                        user_id=1))
# session.commit()
#
# session.add(Instrument(name="Guitar",
#                        description="It's a guitar.",
#                        category_name="Strings",
#                        user_id=2))
# session.commit()
#
# session.add(Instrument(name="Oboe",
#                        description="It's an oboe.",
#                        category_name="Woodwinds",
#                        user_id=1))
# session.commit()
#
# session.add(Instrument(name="French Horn",
#                        description="It's a french horn.",
#                        category_name="Brass",
#                        user_id=1))
# session.commit()
#
# session.add(Instrument(name="Timpani",
#                        description="It's a timpani.",
#                        category_name="Percussion",
#                        user_id=1))
# session.commit()
#
# session.add(Instrument(name="Flute",
#                        description="It's a flute.",
#                        category_name="Woodwinds",
#                        user_id=2))
# session.commit()
