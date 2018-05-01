import string
import random
import json
import requests
from oauth2client import client

# Import database modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Instrument, User, database_info
import sqlalchemy.engine.url
from sqlalchemy.exc import IntegrityError

# Import Flask
from flask import (Flask, render_template, request, redirect, url_for, flash,
                   jsonify, make_response)
from flask import session as login_session

# Initialize Flask app
app = Flask(__name__)

# Connect with database as a session
engine = create_engine(sqlalchemy.engine.url.URL(**database_info))
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


#####################
#  Retrieve pages
#####################

@app.route('/login')
def showLogin():
    if login_session.get('user_id'):
        return redirect(url_for('showLatest'))
    else:
        state = ''.join(random.SystemRandom().choice(
                    string.ascii_uppercase + string.ascii_lowercase +
                    string.digits) for _ in range(64))
        login_session['state'] = state
        next_page = request.args['origin_url']
        return render_template('login.html', STATE=state, NEXT=next_page)


@app.route('/')
@app.route('/catalog')
def showLatest():
    categories = session.query(Category).all()
    latest = session.query(Instrument).order_by(Instrument.id.desc()).limit(10)
    return render_template('latest.html',
                            categories=categories,
                            instruments=latest,
                            user=getUser(),
                            STATE=login_session.get('state'),
                            CURRENT_URL=url_for('showLatest'))


@app.route('/catalog/<category_name>')
def showCategory(category_name):
    categories = session.query(Category).all()
    instruments = session.query(Instrument).filter_by(
                                        category_name=category_name).all()
    return render_template('category.html',
                            categories=categories,
                            category_name=category_name,
                            instruments=instruments,
                            user=getUser(),
                            STATE=login_session.get('state'),
                            CURRENT_URL=url_for('showCategory',
                                                category_name=category_name))


@app.route('/catalog/<category_name>/<instrument_name>')
def showInstrument(category_name, instrument_name):
    categories = session.query(Category).all()
    instrument = session.query(Instrument).filter_by(name=instrument_name,
                                        category_name=category_name).one()
    return render_template('instrument.html',
                            instrument=instrument,
                            categories=categories,
                            user=getUser(),
                            STATE=login_session.get('state'),
                            CURRENT_URL=url_for('showInstrument',
                                            category_name=category_name,
                                            instrument_name=instrument_name))


##########################
#  Login code
##########################

# Google login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token sent by client through URL of POST request
    if (request.args.get('state') != login_session['state']) or (not
            request.headers.get('X-Requested-With')):
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain one-time code from client request body
    auth_code = request.data.decode('utf-8')

    # Exchange one-time code for access token, refresh token, and ID token
    CLIENT_SECRET_FILE = 'client_secret.json'
    credentials = client.credentials_from_clientsecrets_and_code(
        CLIENT_SECRET_FILE,
        ['profile', 'email'],
        auth_code)

    # Store user info and the access token in the session
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = credentials.id_token['sub']
    login_session['email'] = credentials.id_token['email']
    login_session['provider'] = 'google'

    # Retrieve additional user info through Google API call
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    info = requests.get(userinfo_url, params=params).json()
    login_session['username'] = info['name']

    # Check if user exists; if not, create user
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    flash("Successfully logged in")
    return json.dumps({'success': True}), 200, {'contentType': 'application/json'}


# Facebook login
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # Check state token
    if request.args.get('state') != login_session['state']:
        response = make_response(
                json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Exchange short-lived token for long-lived token
    short_token = request.data.decode('utf-8')
    app_info = json.loads(open('fb_client_secrets.json', 'r').read())
    app_id = app_info['web']['app_id']
    app_secret = app_info['web']['app_secret']
    exchange_url = 'https://graph.facebook.com/oauth/access_token?'
    exchange_url += 'grant_type=fb_exchange_token&client_id={}&'.format(app_id)
    exchange_url += 'client_secret={}&fb_exchange_token={}&'.format(app_secret,
                                                          short_token)
    exchange_url += 'redirect_uri=' + url_for('showLogin')
    exchange_result = requests.get(exchange_url).json()

    # Use long-lived token to get user info from API
    long_token = exchange_result.get('access_token')
    info_url = 'https://graph.facebook.com/v2.12/me?'
    info_url += 'access_token={}&fields=name,id,email'.format(long_token)
    info = requests.get(info_url).json()

    # Store info in session
    login_session['provider'] = 'facebook'
    login_session['username'] = info.get('name')
    login_session['email'] = info.get('email')
    login_session['facebook_id'] = info.get('id')
    login_session['access_token'] = long_token

    # Check if user exists; if not, create user
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    flash("Successfully logged in")
    return json.dumps({'success': True}), 200, {'contentType': 'application/json'}


@app.route('/logout')
def disconnect():
    if 'provider' in login_session:
        if login_session.get('provider') == 'google':
            login_session.pop('gplus_id')
        if login_session.get('provider') == 'facebook':
            login_session.pop('facebook_id')
        login_session.pop('access_token')
        login_session.pop('username')
        login_session.pop('email')
        login_session.pop('user_id')
        login_session.pop('provider')
        flash("You have successfully logged out.")
        return redirect(url_for('showLatest'))
    else:
        return redirect(url_for('showLatest'))


###################
#  Edit pages
###################

@app.route('/catalog', methods=['POST'])
def newInstrument():
    # Check state token
    if request.form.get('state') != login_session['state']:
        response = make_response(
                json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check user authorization
    if not login_session.get('user_id'):
        flash("You must be logged in before adding an instrument.")
        return redirect(url_for('showLatest'))
    newInstrument = Instrument(name=request.form['name'],
                         description=request.form['description'],
                         category_name=request.form['category_name'],
                         user_id=login_session.get('user_id'))
    session.add(newInstrument)
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
            return redirect(url_for('showCategory',
                                category_name=request.form['category_name']))


@app.route('/catalog/<category_name>/<instrument_name>', methods=['POST'])
def router(category_name, instrument_name):
    # Check state token
    if request.form.get('state') != login_session['state']:
        response = make_response(
                json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check user authorization
    instrument = session.query(Instrument).filter_by(name=instrument_name,
                                        category_name=category_name).one()
    if instrument.user_id != login_session['user_id']:
        flash("You don't have permission to edit that instrument.")
        return redirect(url_for('showLatest'))
    if request.form['method'] == 'patch':
        return editInstrument(instrument)
    else:
        return deleteInstrument(instrument)


def editInstrument(instrument):
    instrument.name = request.form['name']
    instrument.description = request.form['description']
    instrument.category_name = request.form['category_name']
    session.add(instrument)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        flash('The {} category already has an instrument named {}. \
                Please give your instrument a different name.'.format(
                request.form['category_name'], request.form['name']), 'error')
        return redirect(url_for('showInstrument',
                                category_name=instrument.category_name,
                                instrument_name=instrument.name))
    else:
        flash('Instrument Edited')
        return redirect(url_for('showInstrument',
                                category_name=request.form['category_name'],
                                instrument_name=request.form['name']))


def deleteInstrument(instrument):
    session.delete(instrument)
    session.commit()
    flash('Instrument Deleted')
    return redirect(url_for('showCategory',
                                category_name=instrument.category_name))


#####################
#  JSON endpoints
#####################

@app.route('/catalog.json')
def catalogJSON():
    instruments = session.query(Instrument).order_by(
                                Instrument.category_name).all()
    return jsonify([i.serialize for i in instruments])


@app.route('/catalog/<category_name>.json')
def categoryJSON(category_name):
    instruments = session.query(Instrument).filter_by(
                                category_name=category_name).all()
    return jsonify([i.serialize for i in instruments])


@app.route('/catalog/<category_name>/<instrument_name>.json')
def instrumentJSON(category_name, instrument_name):
    instrument = session.query(Instrument).filter_by(
                                        name=instrument_name,
                                        category_name=category_name).one()
    return jsonify(instrument.serialize)


######################
#  Helper functions
######################

def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUser():
    if login_session.get('user_id'):
        return session.query(User).filter_by(
                                        id=login_session.get('user_id')).one()
    else:
        return None


###################
#  Init code
###################

if __name__ == '__main__':
    app.secret_key = ''.join(random.SystemRandom().choice(
                string.ascii_uppercase + string.ascii_lowercase +
                string.digits) for _ in range(64))
    app.debug = True
    app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))
