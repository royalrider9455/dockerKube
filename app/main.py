from flask import Flask, request, render_template
import redis

app = Flask(__name__)

import os

REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PORT = os.environ['REDIS_PORT']

POSTGRES_HOST = os.environ['POSTGRES_HOST']
POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PORT = os.environ['POSTGRES_PORT']
POSTGRES_DB = os.environ['POSTGRES_DB']
POSTGRES_PASSWORD = os.environ['PGPASSWORD']

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

# postgresql://username:password@host:port/database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev'

from models import db, TraineerTech

db.init_app(app)
with app.app_context():
    # To create / use database mentioned in URI
    db.create_all()
    db.session.commit()
    demo_record_a = TraineerTech(name="Demo Data 1", tech="Devops", rating="5")
    demo_record_b = TraineerTech(name="Demo Data 2", tech="Docker", rating="6")
    demo_record_c = TraineerTech(name="Demo Data 3", tech="Python", rating="7")
    demo_record_d = TraineerTech(name="Demo Data 4", tech="Kubernetes", rating="8")
    demo_record_e = TraineerTech(name="Demo Data 5", tech="Jenkins", rating="9")
    db.session.add(demo_record_a)
    db.session.add(demo_record_b)
    db.session.add(demo_record_c)
    db.session.add(demo_record_d)
    db.session.add(demo_record_e)
    db.session.commit()

red = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/save", methods=['POST'])
def save():
    name = str(request.form['name']).lower()
    tech = str(request.form['tech']).lower()
    rating = str(request.form['rating']).lower()

    # check if data of the name already exists in the redis
    if red.hgetall(name).keys():
        print("hget name:", red.hgetall(name))
        # return a msg to the template, saying the user already exists(from redis)
        return render_template('index.html', user_exists=1, msg='(From Redis)', name=name, tech=red.hget(name,"tech").decode('utf-8'), rating=red.hget(name,"rating").decode('utf-8'))

    # if not in redis, then check in db
    elif len(list(red.hgetall(name)))==0:
        record =  TraineerTech.query.filter_by(name=name).first()
        print("Records fecthed from db:", record)
        
        if record:
            red.hset(name, "tech", tech)
            red.hset(name, "rating", rating)
            # return a msg to the template, saying the user already exists(from database)
            return render_template('index.html', user_exists=1, msg='(Existing records from DataBase)', name=name, tech=record.tech, rating=record.rating)

    # if data of the username doesnot exist anywhere, create a new record in DataBase and store in Redis also
    # create a new record in DataBase
    new_record = TraineerTech(name=name, tech=tech, rating=rating)
    db.session.add(new_record)
    db.session.commit()

    # store in Redis also
    red.hset(name, "tech", tech)
    red.hset(name, "rating", rating)

    # cross-checking if the record insertion was successful into database
    record =  TraineerTech.query.filter_by(name=name).first()
    print("Records fetched from db after insert:", record)

    # cross-checking if the insertion was successful into redis
    print("key-values from redis after insert:", red.hgetall(name))

    # return a success message upon saving
    return render_template('index.html', saved=1, name=name, tech=red.hget(name, "tech").decode('utf-8'), rating=red.hget(name, "rating").decode('utf-8'))

@app.route("/keys", methods=['GET'])
def keys():
	records = TraineerTech.query.all()
	names = []
	for record in records:
		names.append(record.name)
	return render_template('index.html', keys=1, names=names)


@app.route("/get", methods=['POST'])
def get():
	name = request.form['name']
	print("name:", name)
	user_data = red.hgetall(name)
	print("GET Redis:", user_data)

	if not user_data:
		record = TraineerTech.query.filter_by(name=name).first()
		print("GET Record:", record)
		if not record:
			print("No data in redis or db")
			return render_template('index.html', no_record=1, msg=f"No rcords found for {name}")
		red.hset(name, "tech", record.tech)
		red.hset(name, "rating", record.rating)
		return render_template('index.html', get=1, msg="(From DataBase)",name=name, tech=record.tech, rating=record.rating)
	return render_template('index.html',get=1, msg="(From Redis)", name=name, tech=user_data[b'tech'].decode('utf-8'), rating=user_data[b'rating'].decode('utf-8'))