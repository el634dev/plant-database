from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
import certifi

############################################################
# SETUP
############################################################

app = Flask(__name__)

ca = certifi.where()
uri = "mongodb+srv://el634dev:iJgR2SvVfZWQPng8@cluster0.mutz356.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, tlsCAFile=ca)
# Grab the database
db = client.plants_database

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """Display the plants list page."""
    # Replace the following line with a database call to retrieve *all*
    # plants from the Mongo database's `plants` collection.
    plants_data = db.plants_collection.find()

    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)

# ----------------------------------
# About Page
@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

# ----------------------------------
# Plant Creation Page
@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':
        #Get the new plant's name, variety, photo, & date planted, and
        # store them in the object below.
        new_plant = {
            'name': request.form.get('plant_name'),
            'variety': request.form.get('variety'),
            'photo_url': request.form.get('photo'),
            'date_planted': request.form.get('date_planted')
        }
        # Make an `insert_one` database call to insert the object into the
        # database's `plants` collection, and get its inserted id.
        insert = db.plants_collection.insert_one(new_plant)
        # Pass the inserted id into the redirect call below.
        return redirect(url_for('detail', plant_id=insert.inserted_id))
    else:
        context = {
            "plant": plants_list
        }
        return render_template('create.html', **context)

# ------------------------------
# Plant Details
@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""
    # Replace the following line with a database call to retrieve *one*
    # plant from the database, whose id matches the id passed in via the URL.
    plant_to_show = db.plants_collection.find_one({ '_id': ObjectId(plant_id) })

    #  Use the `find` database operation to find all harvests for the
    # plant's id.
    # HINT: This query should be on the `harvests` collection, not the `plants`
    # collection.
    harvest_to_find = db.harvest_collection.find()

    context = {
        'plant' : plant_to_show,
        'harvests': harvest_to_find
    }
    return render_template('detail.html', **context)

# -----------------------------------------------
# POST request for 1 harvest
@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """
    # Create a new harvest object by passing in the form data from the
    # detail page form.
    quantity = request.form['harvested_amount']
    date_planted = request.form.get('date_planted')

    new_harvest = {
        'quantity': quantity, # e.g. '3 tomatoes'
        'date': date_planted,
        'plant_id': plant_id
    }

    # Make an `insert_one` database call to insert the object into the
    # `harvests` collection of the database.
    harvest_insert = db.harvest_collection.insert_one(new_harvest)
    return redirect(url_for('detail', plant_id=harvest_insert.inserted_id))

# ----------------------------------------------------
# Show edit page and an accepted POST request
@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':
        # Make an `update_one` database call to update the plant with the
        # given id. Make sure to put the updated fields in the `$set` object.
        name = request.form['plant_name']
        plant_variety = request.form['variety']
        plant_photo = request.form['photo']
        date_planted = request.form['date_planted']

        edit_plant_details = {
            'name': name,
            'variety': plant_variety,
            'photo': plant_photo,
            'date': date_planted
        }

        search_param = { 'id': ObjectId(plant_id) }
        change_param = {'$set': edit_plant_details}
        db.plants_database.update_one(search_param, change_param)
        return redirect(url_for('detail', plant_id=plant_id))
    else:
        # Make a `find_one` database call to get the plant object with the
        # passed-in _id.
        plant_to_show = db.plants_collection.find_one({ '_id': ObjectId(plant_id) })

        context = {
            'plant': plant_to_show
        }

        return render_template('edit.html', **context)

# ----------------------------------------------------
# Delete Plant_id
@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    """Delete one plant or all harvests with a given plant"""
    # Make a `delete_one` database call to delete the plant with the given
    # id.
    search_param = {"_id": ObjectId(plant_id)}
    db.plants_collection.delete_one(search_param)
    # Also, make a `delete_many` database call to delete all harvests with
    # the given plant id.
    db.harvest_collection.delete_many({"plant_id": plant_id})
    return redirect(url_for('plants_list'))

#-----------------------------------
if __name__ == '__main__':
    app.run(debug=True)
