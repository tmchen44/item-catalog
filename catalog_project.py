# Import database modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Instrument, User, database_info
import sqlalchemy.engine.url
from sqlalchemy.exc import IntegrityError
import string
import random

# Import Flask
from flask import (Flask, render_template, request, redirect, url_for, flash,
                   jsonify)
app = Flask(__name__)

# Connect with database as a session
engine = create_engine(sqlalchemy.engine.url.URL(**database_info))
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog')
def showLatest():
    categories = session.query(Category).all()
    latest = session.query(Instrument).order_by(Instrument.id.desc()).limit(10)
    # if login_session.get('user_id'):
    #     return render_template('latest_private.html', c=categories, i=latest)
    # else:
    return render_template('latest.html',
                            categories=categories,
                            instruments=latest,
                            user=1)


@app.route('/catalog/<category_name>')
def showCategory(category_name):
    categories = session.query(Category).all()
    instruments = session.query(Instrument).filter_by(
                                        category_name=category_name).all()
    return render_template('category.html',
                            categories=categories,
                            category_name=category_name,
                            instruments=instruments,
                            user=1)


@app.route('/catalog/<category_name>/<instrument_name>')
def showInstrument(category_name, instrument_name):
    categories = session.query(Category).all()
    instrument = session.query(Instrument).filter_by(name=instrument_name,
                                        category_name=category_name).one()
    return render_template('instrument.html',
                            instrument=instrument,
                            categories=categories,
                            user=1)


@app.route('/catalog', methods=['POST'])
def newInstrument():
    newItem = Instrument(name=request.form['name'],
                         description=request.form['description'],
                         category_name=request.form['category_name'],
                         user_id=1)
    session.add(newItem)
    # handle database exception for bad category, instrument name
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        message = 'The {} category already has an instrument named {}. \
                    Please give your instrument a different name.'.format(
                    request.form['category_name'], request.form['name'])
        flash(message, 'error')
    else:
        flash('Instrument Added')
    finally:
        if request.form['origin'] == 'latest':
            return redirect(url_for('showLatest'))
        else:
            return redirect(url_for('showCategory', category_name=request.form['category_name']))


@app.route('/catalog/<category_name>/<instrument_name>', methods=['POST'])
def router(category_name, instrument_name):
    if request.form['method'] == 'patch':
        return editInstrument(category_name, instrument_name)
    else:
        return deleteInstrument(category_name, instrument_name)


def editInstrument(category_name, instrument_name):
    editItem = session.query(Instrument).filter_by(name=instrument_name,
                                        category_name=category_name).one()
    editItem.name = request.form['name']
    editItem.description = request.form['description']
    editItem.category_name = request.form['category_name']
    session.add(editItem)
    # handle database exception for bad category, instrument name
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        flash('The {} category already has an instrument named {}. \
                Please give your instrument a different name.'.format(
                request.form['category_name'], request.form['name']), 'error')
        return redirect(url_for('showInstrument',
                                category_name=category_name,
                                instrument_name=instrument_name))
    else:
        flash('Instrument Edited')
        return redirect(url_for('showInstrument',
                                category_name=request.form['category_name'],
                                instrument_name=request.form['name']))


def deleteInstrument(category_name, instrument_name):
    item = session.query(Instrument).filter_by(name=instrument_name,
                                        category_name=category_name).one()
    session.delete(item)
    session.commit()
    flash('Instrument Deleted')
    return redirect(url_for('showCategory', category_name=category_name))

# @app.route('/restaurants/JSON/')
# def restaurantJSON():
#     restaurants = session.query(Restaurant).all()
#     return jsonify(Restaurants=[r.serialize for r in restaurants])
#
# @app.route('/restaurant/<int:restaurant_id>/menu/JSON/')
# def restaurantMenuJSON(restaurant_id):
#     items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
#     return jsonify(MenuItems=[i.serialize for i in items])
#
# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
# def menuItemJSON(restaurant_id, menu_id):
#     item = session.query(MenuItem).filter_by(id=menu_id, restaurant_id=restaurant_id).one()
#     return jsonify(MenuItem=item.serialize)


if __name__ == '__main__':
    app.secret_key = ''.join(random.SystemRandom().choice(
                string.ascii_uppercase + string.digits) for _ in range(64))
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
