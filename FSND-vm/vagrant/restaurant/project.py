import random
import string
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


__author__ = "Harry Staley <staleyh@gmail.com>"
__version__ = "1.0"

app = Flask(__name__)
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# JSON REQUEST HANDLERS
@app.route('/restaurant/JSON')
def RestaurntsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(RestData=[rest.serialize for rest in restaurants])


@app.route('/restaurant/<int:restaurant_id>/JSON')
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def MenuJSON(restaurant_id):
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id
                                              ).all()
    return jsonify(MenuItems=[item.serialize for item in items])


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/JSON')
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def ItemJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id
                                             ).one()
    return jsonify(MenuItem=item.serialize)


# MAIN HANDLERS
@app.route('/')
@app.route('/restaurant/')
def GetRestaurants():
    """
    Get all of the restaurants in the database and display them in a web page.
    """
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)


@app.route('/login/')
def GetLogin():
    """
    Creates a state token and store it in a session for later retrieval to
    guard against cross site forgerty.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits
                                  ) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html')


@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def GetMenu(restaurant_id):
    """ This method gets all of the menu items for the selected restaurant """
    restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                     ).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id
                                              ).all()
    return render_template('menu.html', restaurant=restaurant,
                           items=items)


@app.route('/restaurant/new/', methods=['GET', 'POST'])
def NewRestaurant():
    """ method to add a new restaurant """
    if request.method == 'POST':
        newRestaurant = Restaurant(name=request.form['name'])
        session.add(newRestaurant)
        session.commit()
        flash(str(newRestaurant.name) + " restaurant created.")
        return redirect(url_for('GetRestaurants'))
    else:
        return render_template('newrestaurant.html')


@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def EditRestaurant(restaurant_id):
    """ method to edit a restaurant """
    """ method to edit a menu item """
    restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                     ).one()
    if request.method == 'POST':
        if request.form['name']:
            restaurant.name = request.form['name']
            session.add(restaurant)
            session.commit()
            flash(str(restaurant.name) + " restaurant updated.")
        return redirect(url_for('GetRestaurants'))
    else:
        return render_template('editrestaurant.html', restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def DeleteRestaurant(restaurant_id):
    """ method to delete a restaurant """
    """ method to delete the menu item """
    restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                     ).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id
                                              ).all()
    if request.method == 'POST':
        session.delete(restaurant, items)
        session.commit()
        flash(str(restaurant.name) + " restaurant deleted.")
        return redirect(url_for('GetRestaurants'))
    else:
        return render_template('deleterestaurant.html', restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/newitem', methods=['GET', 'POST'])
def NewMenuItem(restaurant_id):
    """ method to add a new menu item to the menu """
    restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                     ).one()
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'],
                           course=request.form['course'],
                           description=request.form['description'],
                           price=request.form['price'],
                           restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash(str(newItem.name) + " menu item created.")
        return redirect(url_for('GetMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def EditMenuItem(restaurant_id, menu_id):
    """ method to edit a menu item """
    restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                     ).one()
    item = session.query(MenuItem).filter_by(id=int(menu_id)
                                             ).one()
    if request.method == 'POST':
        editItem = item
        if request.form['name']:
            editItem.name = request.form['name']
            editItem.course = request.form['course']
            editItem.description = request.form['description']
            editItem.price = request.form['price']
            session.add(editItem)
            session.commit()
            flash(str(item.name) + " updated.")
        return redirect(url_for('GetMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant=restaurant,
                               item=item)


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete',
           methods=['GET', 'POST'])
def DeleteMenuItem(restaurant_id, menu_id):
    """ method to delete the menu item """
    restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                     ).one()
    item = session.query(MenuItem).filter_by(id=int(menu_id)
                                             ).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Menu item deleted.")
        return redirect(url_for('GetMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html', restaurant=restaurant,
                               item=item)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
