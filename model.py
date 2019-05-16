"""BayArt - Bay Area Art Connection Project: db.Model classes"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from flask import Flask

from random import randint
import datetime

from faker import Faker
fake = Faker()


class User(db.Model):
    """User class"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_name = db.Column(db.String(50))
    password = db.Column(db.String(30))
    email = db.Column(db.String(50))
    last_active = db.Column(db.DateTime, nullable = True)
    hourly_rate = db.Column(db.Integer, nullable = True)
    link_to_website = db.Column(db.String(50), nullable = True)

    def __repr__(self):
        """Provides the representaion of a User instance when printed"""

        return f"<User user_id={self.user_id} user_name={self.user_name}>"

    posts = db.relationship("Post",
                           backref=db.backref("users"))

    tags = db.relationship("Tag", secondary="users_tags", backref="users")


class Post(db.Model):
    """Post class, to create a new post ("listing") on the website."""

    __tablename__ = "posts"

    post_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    description = db.Column(db.String(30))
    zipcode = db.Column(db.Integer, db.ForeignKey("zipcodes.valid_zipcode"))

    # tags = db.relationship("Tag", secondary="posts_tags", backref="posts")

    def __repr__(self):
        """Provides the representaion of a Post instance when printed"""

        return f"<Post post_id={self.post_id} user_id={self.user_id}>"

    tags = db.relationship("Tag", secondary="posts_tags", backref="posts")

    zipcodes = db.relationship("Zipcode", backref=db.backref("posts"))

class Tag(db.Model):
    """Tag class, creates new tags to be used in posts & users."""

    __tablename__ = "tags"

    tag_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tag_name = db.Column(db.String(50))


    def __repr__(self):
        """Provides the representaion of a Tag instance when printed"""

        return f"<Tag tag_id={self.tag_id} tag_name={self.tag_name}>"


class Zipcode(db.Model):
    """Contains a list of all valid zipcodes in the Bay Area."""

    __tablename__ = "zipcodes"

    valid_zipcode = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        """Provides the representaion of a Zipcode instance when printed"""

        return f"<Zipcode valid_zipcode={self.valid_zipcode}>"


posts_tags = db.Table(
    "posts_tags",
    db.metadata,
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.tag_id")),
    db.Column("post_id", db.Integer, db.ForeignKey("posts.post_id"))
)

users_tags = db.Table(
    "users_tags",
    db.metadata,
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.tag_id")),
    db.Column("user_id", db.Integer, db.ForeignKey("users.user_id"))
)

#####################################################################
#These functions help create the database.

def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///bayart'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


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
        all_zips = db.session.query().all()
        fzipcode = all_zips[i]
        fpost = Post(user_id=fuser_id, description=fdescription,
            zipcode=fzipcode) 
    print("Commiting all new posts.")
    db.session.commit()


def seed_zipcodes():
    file = open("non_server_files/raw_zipcodes.txt")
    text = file.read()
    file.close()
    words = text.split('>')
    shorter_list = []
    final_list = set()

    for word in words:
        try:
            to_add = word[0].isdigit()  
        except:
            to_add = False
        if to_add:
            shorter_list.append(word[:5])

    for code in shorter_list:
        if code.isdigit():
            final_list.add(code)
            # if code not in shorter_list:

    for zip_code in final_list:
        new_zcode = Zipcode(valid_zipcode=zip_code)
        db.session.add(new_zcode)

    db.session.commit()


if __name__ == "__main__":
    from server import app

    connect_to_db(app)
    print("Connected to the database!")