"""BayArt - Bay Area Art Connection Project: db.Model classes"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

db = SQLAlchemy()

from flask import Flask

from random import randint
from datetime import datetime

from faker import Faker
fake = Faker()


class User(UserMixin, db.Model):
    """User class"""

    __tablename__ = "users"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_name = db.Column(db.String(50), unique=True)
    is_artist = db.Column(db.Boolean, unique=False, default=False)
    password = db.Column(db.String(30))
    email = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(30))
    last_active = db.Column(db.DateTime, nullable = True)
    hourly_rate = db.Column(db.Integer, nullable = True)
    show_unpaid = db.Column(db.Boolean, unique=False, default=False)
    link_to_website = db.Column(db.String(50), nullable = True)
    bio = db.Column(db.String(500), nullable = True)
    unavail_mon = db.Column(db.Boolean, default=False)
    unavail_tues = db.Column(db.Boolean, default=False)
    unavail_wed = db.Column(db.Boolean, default=False)
    unavail_thurs = db.Column(db.Boolean, default=False)
    unavail_fri = db.Column(db.Boolean, default=False)
    unavail_sat = db.Column(db.Boolean, default=False)
    unavail_sun = db.Column(db.Boolean, default=False)

    def __repr__(self):
        """Provides the representaion of a User instance when printed"""

        return f"<User id={self.id} user_name={self.user_name}>"

    posts = db.relationship("Post",
                           backref=db.backref("users"))

    tags = db.relationship("Tag", secondary="users_tags", backref="users")


class Post(db.Model):
    """Post class, to create a new post ("listing") on the website."""

    __tablename__ = "posts"

    post_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_title = db.Column(db.String(50))
    description = db.Column(db.String(1250))
    post_date = db.Column(db.DateTime)
    gig_date = db.Column(db.String(100))
    isfixed = db.Column(db.Boolean, default=False)
    ishourly = db.Column(db.Boolean, default=False)
    pay = db.Column(db.Integer, nullable=True)
    # If isfixed is True, ishourly must be false.
    # If ishourly is True, is fixed must be false.
    # If both isfixed and ishourly are false, pay will not display on page,
    # and "Rate Negotiable" will display instead.
    # Pay will be a dollar ammount, attached to either fixed budget,
    # or hourly pay.
    filled = db.Column(db.Boolean, default=False)

    zipcode = db.Column(db.Integer, db.ForeignKey("zipcodes.valid_zipcode"),
                        nullable = False)

    # tags = db.relationship("Tag", secondary="posts_tags", backref="posts")

    def __repr__(self):
        """Provides the representaion of a Post instance when printed"""

        return f"<Post post_id={self.post_id} post_title={self.post_title} user_id={self.user_id}>"

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


class Unavailability(db.Model):
    """Takes a user id and dates objects for unavailable"""

    __tablename__ = "unavailability"

    un_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date_ranges = db.Column(db.String(50))

    def __repr__(self):
        """Provides the representaion of an Unavailability instance when printed"""

        return f"<Unavailabilty tag_id={self.user_id} tag_name={self.date_ranges}>"

    users = db.relationship("User", backref=db.backref("unavailabilty"))


class Zipcode(db.Model):
    """Contains a list of all valid zipcodes in the Bay Area."""

    __tablename__ = "zipcodes"

    valid_zipcode = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(100))

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
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"))
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


def seed_users():
    """Creates a series of fake posts. Must seed BEFORE posts."""

    for i in range(1, 51):
        fname = fake.name()
        fpassword = randint(1, 9)
        fpassword += i
        fbio = fake.sentence() + " " + fake.sentence()
        fhourly_rate = randint(16, 125)
        fartistnum = randint(0, 1)
        
        fphone_list = str(randint(1111111111, 9999999999))
        count = 0
        fphone = "("
        for num in fphone_list:
            if count == 3:
                fphone += ') '
                fphone += num
                count += 1
            elif count == 6:
                fphone += '-'
                fphone += num
                count += 1
            else:
                fphone += num
                count += 1

        if fartistnum == 0:
            fartist = False
        else:
            fartist = True
        femail = (fname[:3] + fname[-2:] + str(i) + '@gmail.com')
        flast_active = fake.date_between(start_date="-1y", end_date="today")
        fuser = User(user_name=fname, is_artist=fartist, password=fpassword, bio=fbio,
                hourly_rate=fhourly_rate, phone=fphone, email=femail,
                last_active=flast_active)
        db.session.add(fuser) 
    print("Commiting all new users.")
    db.session.commit()



def seed_posts():
    """Creates a series of fake posts. Must seed AFTER zipcodes and users."""
    for i in range(1, 35):
        fuser_id = randint(1,50)
        fpost_date = fake.date_between(start_date="-3y", end_date="today")
        is_pay = randint(0,1)
        if is_pay == 0:
            fpay = None
        else:
            fpay = randint(30,2000)
        fpone = fake.name()
        fpost_title = fpone[:4] + '. This is the title of this post!'
        fdescription = fake.sentence() + " " + fake.sentence()
        fzipcodes = db.session.query(Zipcode.valid_zipcode).all()
        fzipcode = fzipcodes[i]
        fpost = Post(user_id=fuser_id, description=fdescription,
            zipcode=fzipcode, post_title=fpost_title, post_date=fpost_date,
            pay=fpay)
        db.session.add(fpost)
    print("Commiting all new posts.")
    db.session.commit()


def seed_tags():
    """Seeds tags as listed below:"""
    tag_list = ['Photography', 'Cinematography', 'Video Editing', 'Music',
                'Audio Recording', 'Dance', 'Acting', 'Graphic Design']

    for category in tag_list:
        tag_to_add = Tag(tag_name=category)
        db.session.add(tag_to_add)

    db.session.commit()


def seed_zipcodes():
    """Strips zipcodes from raw html txt file and adds to database.
    Must seed BEFORE posts."""
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

    names_file = open("non_server_files/zip_code_database_placenames.csv")
    names_text = names_file.readlines()
    names_file.close()
    zip_dict = {}

    for names_line in names_text:
        names_line_split = names_line.split(',')
        zip_dict[names_line_split[0]] = names_line_split[3]

    zip_list = list(final_list)

    final_dict = {}

    for k, v in zip_dict.items():
        if k in zip_list:
            final_dict[k] = v

    for k, v in final_dict.items():
        nv = v.replace('"', '')
        new_zcode = Zipcode(valid_zipcode=k, location_name=nv)
        db.session.add(new_zcode)

    db.session.commit()


def seed_all():
    db.create_all()
    seed_zipcodes()
    seed_tags()
    seed_users()
    seed_posts()



if __name__ == "__main__":
    from server import app

    connect_to_db(app)
    print("Connected to the database!")
