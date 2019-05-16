"""BayArt - Bay Area Art Connection Project
This file will create a host of fake users and posts"""
from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from model import Zipcode
from model import User
from model import Post

from random import randint
db = SQLAlchemy()

from faker import Faker
fake = Faker()

# import pdb
# pdb.set_trace()

def seed_user():
    for i in range(1, 51):
        fname = fake.name()
        fpassword = randint(1, 9)
        fpassword += i
        fhourly_rate = randint(16, 125)
        femail = (fname[:3] + fname[-2:] + '@gmail.com')
        fuser = User(user_name=fname, password=fpassword,
                hourly_rate=fhourly_rate, email=femail)
        db.session.add(fuser) 
    print("Commiting all new users.")
    db.session.commit()



def seed_posts():
    for i in range(1, 35):
        fuser_id = randint(1,50)
        fdescription = fake.sentence()
        fzipcode = session.query(Zipcode).get(i)
        fzipcode = fzipcode.valid_zipcode
        fpost = Post(user_id=fuser_id, description=fdescription,
            zipcode=fzipcode) 
    print("Commiting all new posts.")
    db.session.commit()