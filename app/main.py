from flask import Flask, request, render_template

app = Flask(__name__)

import os

POSTGRES_HOST = os.environ['POSTGRES_HOST']
POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PORT = os.environ['POSTGRES_PORT']
POSTGRES_DB = os.environ['POSTGRES_DB']
POSTGRES_PASSWORD = os.environ['PGPASSWORD']

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

# postgresql://username:password@host:port/database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://docker_kube:docker_kube@db:5432/docker_kube_dev'

from models import db, UserFavs

db.init_app(app)
with app.app_context():
    # To create / use database mentioned in URI
    db.create_all()
    db.session.commit()


@app.route("/")
def main():
    return render_template('index.html')

@app.route("/save", methods=['POST'])
def save():
    username = str(request.form['username']).lower()
    place = str(request.form['place']).lower()
    food = str(request.form['food']).lower()

    record =  UserFavs.query.filter_by(username=username).first()
        
    if record:
        # return a msg to the template, saying the user already exists(from database)
        return render_template('index.html', user_exists=1, msg='(From DataBase)', username=username, place=record.place, food=record.food)

    # if data of the username doesnot exist anywhere, create a new record in DataBase
    # create a new record in DataBase
    new_record = UserFavs(username=username, place=place, food=food)
    db.session.add(new_record)
    db.session.commit()

    # cross-checking if the record insertion was successful into database
    record =  UserFavs.query.filter_by(username=username).first()
    print("Records fetched from db after insert:", record)

    # return a success message upon saving
    
    return render_template('index.html', saved=1, username=username, place=record.place, food=record.food)

@app.route("/keys", methods=['GET'])
def keys():
	records = UserFavs.query.all()
	names = []
	for record in records:
		names.append(record.username)
	return render_template('index.html', keys=1, usernames=names)


@app.route("/get", methods=['POST'])
def get():
	username = request.form['username']
	print("Username:", username)
        
	existing_record = UserFavs.query.filter_by(username=username).first()
    

	if not existing_record:		
		return render_template('index.html', no_record=1, msg=f"Record not yet defined for {username}")
		
	return render_template('index.html', get=1, msg="(From DataBase)",username=username, place=existing_record.place, food=existing_record.food)