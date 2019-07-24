#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, \
    jsonify, url_for, flash
import uuid
from flask import session as login_session
from flask_login import login_required, current_user
from micawber.providers import bootstrap_basic
from micawber.contrib.mcflask import add_oembed_filters
from oauth2client.client import flow_from_clientsecrets, verify_id_token
from oauth2client.client import FlowExchangeError
from bs4 import BeautifulSoup
from slugify import slugify
import os
from flask import make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item
import httplib2
import json
import requests
import random
import string

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

APP_PATH = os.path.dirname(os.path.abspath(__file__))

CLIENT_ID = json.loads(open("client_secret.json",
                            "r").read())['web']['client_id']

print(CLIENT_ID)

app = Flask(__name__)

oembed_providers = bootstrap_basic()
add_oembed_filters(app, oembed_providers)


# JSON APIs to view Category Information
@app.route('/<category_slug>/item/JSON')
def category_catalog_json(category_slug):
    session = DBSession()
    category = session.query(Category).filter_by(slug=category_slug).one()
    items = session.query(Item).filter_by(category_slug=category_slug).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/category/item/<item_slug>/JSON')
def item_json(category_id, item_id):
    session = DBSession()


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
    return render_template('index.html', categories=categories, items=items)


# Show all items in a category
@app.route('/catalog/<category_slug>/items', methods=['GET'])
def show_cat_items(category_slug):
    session = DBSession()
    cat = session.query(Category).filter(Category.slug == category_slug).one()
    items = session.query(Item).filter(Item.category_id == cat.id).all()
    return render_template("items.html", items=items, category=cat)


# View a single item's details.
@app.route('/catalog/<category_slug>/<item_slug>/',
           methods=['GET'])
def show_item(item_slug, category_slug):
    session = DBSession()
    cat = session.query(Category).filter(Category.slug == category_slug).first()
    item = session.query(Item).filter(Item.slug == item_slug).first()
    return render_template("item.html", item=item, category=cat)
# @app.route('/catalog/<int:restaurant_id>/')
# @app.route('/restaurant/<int:restaurant_id>/menu/')
# def showMenu(restaurant_id):
#     restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
#     items = session.query(MenuItem).filter_by(
#         restaurant_id=restaurant_id).all()
#     return render_template('menu.html', items=items, restaurant=restaurant)


# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def new_category():
    session = DBSession()
    # @login_required
    # if 'username' not in login_session:
    #     return redirect('/signin')
    if request.method == 'POST':
        new_category = Category(name=request.form['name'],
                                slug=slugify(request.form['name']))
        session.add(new_category)
        flash('New Category %s Successfully Created' % new_category.name)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template('new_category.html')


# Edit a category
@app.route('/catalog/<category_slug>/edit/', methods=['GET', 'POST'])
def edit_category(category_slug):
    # @login_required
    session = DBSession()
    editedCategory = session.query(
        Category).filter_by(slug=category_slug).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category Successfully Edited %s' % editedCategory.name)
            return redirect(url_for('show_categories'))
    else:
        return render_template('edit_category.html', category=editedCategory)


# Delete a category
@app.route('/catalog/<category_slug>/delete/', methods=['GET', 'POST'])
# @login_required
def delete_category(category_slug):
    session = DBSession()
    DBSession = sessionmaker(bind=engine)
    categoryToDelete = session.query(
        Category).filter_by(slug=category_slug).one()
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('show_items', category_slug=category_slug))
    else:
        return render_template('deleteCategory.html',
                               category=categoryToDelete)


# Create a new catalog item
@app.route('/catalog/item/new/', methods=['GET', 'POST'])
@login_required
def new_item():
    session = DBSession()
    if request.method == 'POST':
        new_item = Item(name=request.form['name'],
                        slug=slugify(request.form['name']),
                        description=request.form['description'],
                        category_id=request.form['category'])
        session.add(new_item)
        session.commit()
        flash('New Catalog %s Item Successfully Created' % (new_item.name))
        return redirect(url_for('show_categories'))
    else:
        categories = session.query(Category).all()
        return render_template('new_item.html', categories=categories)


# Edit an item
@app.route('/catalog/<item_slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_slug):
    session = DBSession()
    editedItem = session.query(Item).filter_by(slug=item_slug).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
            editedItem.slug = slugify(request.form['name'])
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            editedItem.description = request.form['category']
        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('show_categories'))
    else:
        categories = session.query(Category).all()
        return render_template('edit_item.html',
                               category_id=category_id,
                               item_id=item_id,
                               item=editedItem,
                               categories=categories)


# Delete a item
@app.route('/catalog/<item_slug>/delete',
           methods=['GET', 'POST'])
@login_required
def delete_item(item_slug):
    session = DBSession()
    itemToDelete = session.query(Item).filter_by(slug=item_slug).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Catalog Item Successfully Deleted')
        return redirect(url_for('show_categories'))
    else:
        return render_template('deleteItem.html', item=itemToDelete)


@app.route('/signin')
def signin():
    state = uuid.uuid4()
    login_session['state'] = str('state')
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
    login_session['access_token'] = access_token
    # login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
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
