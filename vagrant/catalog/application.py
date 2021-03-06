#!/usr/bin/env python3

from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   jsonify,
                   url_for,
                   flash,
                   g)
import uuid
from flask import session as login_session
"""from flask_login import (login_required,
                        #  current_user,
                        #  login_user,
                        #  LoginManager)
                        """
from micawber.providers import bootstrap_basic
from micawber.contrib.mcflask import add_oembed_filters
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from oauth2client.client import flow_from_clientsecrets, verify_id_token
from oauth2client.client import FlowExchangeError
from bs4 import BeautifulSoup
from slugify import slugify
import os
from flask import make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
import httplib2
import json
import requests
# import random
import string

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)
APP_PATH = os.path.dirname(os.path.abspath(__file__))
auth = HTTPBasicAuth()
oembed_providers = bootstrap_basic()
add_oembed_filters(app, oembed_providers)


@auth.verify_password
def verify_password(username_or_token, password):
    # check to see if it's a token first
    session = DBSession()
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id=user_id).one()
    else:
        user = session.query(User).filter_by(username=username_or_token).\
            first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/token')
@auth.login_required
def get_auth_token():
    session = DBSession()
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@app.route('/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        print("missing arguments")
        abort(400)

    if session.query(User).filter_by(username=username).first() is not None:
        return jsonify({'message': 'user already exists'})

    user = User(username=username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({'username': user.username})


# JSON APIs to view categories
@app.route('/catalog.json')
def catalog_json():
    session = DBSession()
    categories = session.query(Category).all()
    items = session.query(Item).all()
    return jsonify(Category=[c.serialize for c in categories],
                   Items=[i.serialize for i in items])


# JSON APIs to view Category Information
@app.route('/<category_slug>/item/JSON')
def category_catalog_json(category_slug):
    session = DBSession()
    category = session.query(Category).filter_by(slug=category_slug).one()
    items = session.query(Item).filter_by(category_slug=category_slug).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/category/JSON')
def categories_json():
    session = DBSession()
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# Show all categories
@app.route('/')
@app.route('/category/')
def show_categories():
    session = DBSession()
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).all()
    return render_template('index.html',
                           categories=categories,
                           items=items)


# Show all items in a category
@app.route('/catalog/<category_slug>/items', methods=['GET'])
def show_cat_items(category_slug):
    session = DBSession()
    cats = session.query(Category).order_by(asc(Category.name))
    cat = session.query(Category).filter(Category.slug == category_slug).one()
    items = session.query(Item).filter(Item.category_id == cat.id)\
        .limit(5).all()
    return render_template("items.html",
                           categories=cats,
                           items=items,
                           category=cat)


# View a single item's details.
@app.route('/catalog/<category_slug>/<item_slug>',
           methods=['GET'])
def show_item(item_slug, category_slug):
    session = DBSession()
    cat = session.query(Category).filter(Category.slug == category_slug)\
        .first()
    item = session.query(Item).filter(Item.slug == item_slug).first()
    return render_template("item.html", item=item, category=cat)

# Create a new category


@app.route('/category/new/', methods=['GET', 'POST'])
@auth.login_required
def new_category():
    session = DBSession()
    username = (auth.username())
    user = session.query(User).filter(User.username == username)\
        .first()
    user_id = user.id
    # if 'username' not in login_session:
    #     return redirect('/signin')
    if request.method == 'POST':
        new_category = Category(name=request.form['name'],
                                slug=slugify(request.form['name']),
                                user_id=user_id)
        session.add(new_category)
        flash('New Category %s Successfully Created' % new_category.name)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template('new_category.html')


# Create a new catalog item
@app.route('/catalog/item/new/', methods=['GET', 'POST'])
@auth.login_required
def new_item():
    session = DBSession()
    username = (auth.username())
    user = session.query(User).filter(User.username == username)\
        .first()
    user_id = user.id
    if request.method == 'POST':
        new_item = Item(name=request.form['name'],
                        slug=slugify(request.form['name']),
                        description=request.form['description'],
                        category_id=request.form['category'],
                        user_id=user_id)
        session.add(new_item)
        session.commit()
        flash('New %s Item Created' % (new_item.name))
        return redirect(url_for('show_categories'))
    else:
        categories = session.query(Category).all()
        return render_template('new_item.html',
                               categories=categories)


# Edit an item
@app.route('/catalog/<item_slug>/edit/', methods=['GET', 'POST'])
@auth.login_required
def edit_item(item_slug):
    session = DBSession()
    editedItem = session.query(Item).filter_by(slug=item_slug).one()
    username = auth.username()
    user = session.query(User).filter(User.username == username)\
        .first()
    user_id = user.id
    if editedItem.user_id == user_id:
        if request.method == 'POST':
            if request.form['name']:
                editedItem.name = request.form['name']
                editedItem.slug = slugify(request.form['name'])
            if request.form['description']:
                editedItem.description = request.form['description']
            if request.form['category']:
                editedItem.category_id = request.form['category']
            session.add(editedItem)
            session.commit()
            flash('Item Successfully Edited')
            return redirect(url_for('show_categories'))
        else:
            if editedItem.user_id == user_id:
                categories = session.query(Category).all()
                return render_template('edit_item.html',
                                       item=editedItem,
                                       categories=categories)
    else:
            flash('Only the item owner can make edits')
            return redirect(url_for('show_categories'))


# Delete a item
@app.route('/catalog/<item_slug>/delete',
           methods=['GET', 'POST'])
@auth.login_required
def delete_item(item_slug):
    session = DBSession()
    username = (auth.username())
    user = session.query(User).filter(User.username == username)\
        .first()
    itemToDelete = session.query(Item).filter_by(slug=item_slug).one()
    if itemToDelete.user_id == user.id:
        if request.method == 'POST':
            session.delete(itemToDelete)
            session.commit()
            flash('Item Successfully Deleted')
            return redirect(url_for('show_categories'))
        else:
            return render_template('delete_item.html',
                                   item=itemToDelete,
                                   user_id=user_id)
    else:
        flash('Only the item owner can delete it')
        return redirect(url_for('show_categories'))


# Edit a category that you created
@app.route('/catalog/edit/<category_slug>/', methods=['GET', 'POST'])
@auth.login_required
def edit_category(category_slug):
    session = DBSession()
    categories = session.query(Category).order_by(asc(Category.name)).all
    editedCategory = session.query(
        Category).filter(Category.slug == category_slug).first()
    username = auth.username()
    user = session.query(User).filter(User.username == username)\
        .first()
    user_id = user.id
    if editedCategory.user_id == user_id:
        if request.method == 'POST':
                if request.form['name']:
                    editedCategory.name = request.form['name']
                    flash('Category Successfully Edited %s'
                          % editedCategory.name)
                    return redirect(url_for('show_categories'))
        else:
            return render_template('edit_category.html',
                                   categories=categories,
                                   category=editedCategory
                                   )
    else:
            flash('Only the category owner can edit it.')
            return redirect(url_for('show_categories'))


# Delete a category that you created
@app.route('/catalog/delete/<category_slug>/', methods=['GET', 'POST'])
@auth.login_required
def delete_category(category_slug):
    session = DBSession()
    categoryToDelete = session.query(Category).\
        filter_by(slug=category_slug).one()
    username = auth.username()
    user = session.query(User).filter(User.username == username)\
        .first()
    user_id = user.id
    if categoryToDelete.user_id == user_id:
        if request.method == 'POST':
            session.delete(categoryToDelete)
            flash('%s Successfully Deleted' % categoryToDelete.name)
            session.commit()
            return redirect(url_for('show_items', category_slug=category_slug))
        else:
            return render_template('delete_category.html',
                                   category=categoryToDelete)
    else:
        flash('Only the category owner can delete it.')
        return redirect(url_for('show_categories'))


@app.route('/signin')
def signin():
    state = uuid.uuid4()
    login_session["state"] = str("state")
    return render_template('signin.html', state=state)


@app.route('/signout')
def signout():
    print(type(login_session))
    del login_session["username"]
    return render_template('signout.html')


@app.route('/gconnect', methods=["POST"])
def gconnect():
    print(request.args.get("state"), " == ", login_session["state"])
    if (str(request.args.get("state")) != str(login_session["state"])):
        print("Invalid State")
        response = make_response(json.dumps("Invalid State parameter"), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    code = request.data
    try:
        print("code", code)
        oauth_flow = flow_from_clientsecrets(os.path.join(
            APP_PATH, "client_secret.json"),
            scope="")
        oauth_flow.redirect_uri = 'postmessage'
        oauth_flow.access_type = 'offline'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError as e:
        print('Authentication has failed: {}'.format(str(e)))
        response = make_response(json.dumps("Failed to upgrade"), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    access_token = credentials.access_token

    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token = %s' %
           access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    print(result)
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print('Token\'s client ID does not match app\'s.')
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data.get('name', '')
    login_session['picture'] = data.get('picture', '')
    login_session['email'] = data['email']

    output = ''
    output += '<h1> Welcome, '
    output += login_session['username']
    output += '! </h1> '
    output += ' <img src = "'
    output += login_session['picture']
    output += '"style = "width: 200px; height: 200px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print('done!')
    return output


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
