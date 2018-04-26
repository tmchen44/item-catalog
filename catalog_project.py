# Import database modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Instrument, User, database_info
import sqlalchemy.engine.url

# Import Flask
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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
    instruments = session.query(Instrument).filter_by(category_name=category_name).all()
    return render_template('category.html',
                            categories=categories,
                            category_name=category_name,
                            instruments=instruments,
                            count=len(instruments),
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

# @app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
# def newMenuItem(restaurant_id):
#     if request.method == 'POST':
#         newItem = MenuItem(name=request.form['name'],
#                            course=request.form['course'],
#                            description=request.form['description'],
#                            price=request.form['price'],
#                            restaurant_id=restaurant_id)
#         session.add(newItem)
#         session.commit()
#         flash("Menu Item Created")
#         return redirect(url_for('showMenu', restaurant_id=restaurant_id))
#     else:
#         return render_template('newmenuitem.html', restaurant_id=restaurant_id)
#
# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
# def editMenuItem(restaurant_id, menu_id):
#     editItem = session.query(MenuItem).filter_by(id=menu_id, restaurant_id=restaurant_id).one()
#     if request.method == 'POST':
#         editItem.name = request.form['name']
#         editItem.course = request.form['course']
#         editItem.description = request.form['description']
#         editItem.price = request.form['price']
#
#         session.add(editItem)
#         session.commit()
#         flash("Menu Item Successfully Edited")
#         return redirect(url_for('showMenu', restaurant_id=restaurant_id))
#     else:
#         return render_template('editmenuitem.html', item=editItem)
#
# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
# def deleteMenuItem(restaurant_id, menu_id):
#     item = session.query(MenuItem).filter_by(id=menu_id).one()
#     if request.method == 'POST':
#         session.delete(item)
#         session.commit()
#         flash("Menu Item Successfully Deleted")
#         return redirect(url_for('showMenu', restaurant_id=restaurant_id))
#     else:
#         return render_template('deletemenuitem.html', item=item)
#
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
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)



# @app.route('/restaurant/new/', methods=['GET', 'POST'])
# def newRestaurant():
#     if request.method == 'POST':
#         newRestaurant = Restaurant(name=request.form['name'])
#         session.add(newRestaurant)
#         session.commit()
#         flash("New Restaurant Created")
#         return redirect(url_for('showRestaurants'))
#     else:
#         return render_template('newrestaurant.html')
#
# @app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
# def editRestaurant(restaurant_id):
#     restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
#     if request.method == 'POST':
#         restaurant.name = request.form['name']
#         session.add(restaurant)
#         session.commit()
#         flash("Restaurant Successfully Edited")
#         return redirect(url_for('showRestaurants'))
#     else:
#         return render_template('editrestaurant.html', restaurant=restaurant)
#
# @app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
# def deleteRestaurant(restaurant_id):
#     restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
#     if request.method == 'POST':
#         session.delete(restaurant)
#         session.commit()
#         flash("Restaurant Successfully Deleted")
#         return redirect(url_for('showRestaurants'))
#     else:
#         return render_template('deleterestaurant.html', restaurant=restaurant)
