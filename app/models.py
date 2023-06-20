from flask_sqlalchemy import SQLAlchemy 

db = SQLAlchemy()

class TraineerTech(db.Model):
	name = db.Column(db.String, primary_key=True)
	tech = db.Column(db.String)
	rating = db.Column(db.String)

	def __init__(self, name, tech, rating):
		self.name=name
		self.tech=tech
		self.rating=rating

	def __repr__(self):
		return f'<Name-Tech-Rating : {self.name}-{self.tech}-{self.rating}'

