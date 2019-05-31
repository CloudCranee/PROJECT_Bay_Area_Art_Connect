from flask import Flask, render_template, request, jsonify, flash, redirect, session, abort, url_for
app=Flask(__name__)
from flask_bootstrap import Bootstrap
from jinja2 import StrictUndefined
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Post, Zipcode, Tag

login_manager = LoginManager()
login_manager.init_app(app)

app.secret_key = "thefriendswemadealongtheway"

app.jinja_env.undefined = StrictUndefined


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()
    ###Do I need to add more code here or is this complete?



@login_manager.unauthorized_handler
def unauthorized_callback():
    """If there is no user logged in,
    this will redirect the client back to the homepage."""
    flash("You will need to log in or create an account before viewing this page.")
    return redirect('/')



@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/artists')
@login_required
def display_artists():
    """Renders a page with all artists info."""

    artists = User.query.filter_by(is_artist=True).order_by(User.last_active.desc())

    return render_template("artists.html", artists=artists)


@app.route('/newpost')
@login_required
def new_post():
    """Renders a page with the option to post a new gig."""

    zipcode_instances = Zipcode.query.all()

    zipcodes = []

    for zipcode in zipcode_instances:
        zipcodes.append(zipcode.valid_zipcode)

    locations = []

    for zipcode in zipcode_instances:
        locations.append(zipcode.location_name)

    locations = list(set(locations))

    locations.sort()

    tags = Tag.query.all()

    return render_template("new_post.html", zipcodes=zipcodes,
                        locations=locations, tags=tags)


@app.route('/creategig', methods=['POST'])
def add_new_gig_to_database():
    """Adds a new gig to the database."""

    user_id = current_user.id
    
    post_title = request.form["post_title"]
    description = request.form["description"]
    location = request.form["location"]
    zipcode = Zipcode.query.filter_by(location_name=location).first()

    post_date = datetime.now()

    new_post = Post(post_title=post_title, description=description,
        zipcode=zipcode.valid_zipcode, post_date=post_date)

    post_tags = request.form.getlist("tag")

    for tag in post_tags:
        associated_tag = Tag.query.get(tag)
        new_post.tags.append(associated_tag)

    db.session.add(new_post)

    db.session.commit()
        
    flash("Thank you. Your new post is now live.")

    return redirect("posts")


@app.route('/posts')
@login_required
def display_posts():
    """Displays a list of all posts
    TODO: (Pinterest style ((AJAX? REACT??)) infinte scroll.
    Sort by most recent post at the top."""

    posts = Post.query.all()

    posts.reverse()

    return render_template("posts.html", posts=posts)


@app.route('/login_form')
def present_login_form():
    """Displays the login form. Eventually I would incorporate this on the 
    homepage"""

    return render_template("login_form.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """form to log in"""

    email = (request.form["email"]).lower()
    password = request.form["password"]
    user = User.query.filter_by(email=email).one_or_none()

    if not user:
        flash("Incorrect email or password.")
        return redirect("/login_form")

    if not check_password_hash(user.password, password):
        flash("Incorrect email or password.")
        return redirect("/login_form")

    if user.is_authenticated:
        login_user(user)

        last_active = datetime.now()
        current_user.last_active = last_active
        db.session.commit()

        flash("You are now logged in.")
        return redirect('/')

    flash("Unexpected Error.")
    return redirect("/login_form")


    # if not user:
    #     flash("No such user")
    #     return redirect("/login")
        
    # if user.password != password:
    #     flash("Incorrect password")
    #     return redirect("/login")

    # login_user(user)
    # flash("You are now logged in.")
    # return redirect(f"/users/{user.id}")

@app.route('/logout')
@login_required
def logout():
    """Logs a user out and redirects to homepage."""


    logout_user()
    flash("You have successfully logged out.")

    return redirect('/')



@app.route('/availability', methods=['GET'])
@login_required
def display_availability_page():
    """Displays and artist's change availability page."""

    daysweek = list(current_user.daysweek)

    return render_template("availability.html", daysweek=daysweek)


@app.route('/changeavailability', methods=['GET', 'POST'])
def change_availability():
    """Changes artist availability in database."""
    
    new_avail = request.form.get("dates")

    print(new_avail)

    current_user.daysweek = new_avail

    db.session.commit()
    
    daysweek = list(new_avail)

    # flash("You have successfully updated your availability.")
    # jsonify([True])
    return redirect('/')


@app.route('/sign_up', methods=['GET'])
def register_form():
    """Show form for user signup."""

    return render_template("register_form.html")



@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    user_name = request.form["user_name"]

    password = request.form["password"]
    password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

    email = (request.form["email"]).lower()
    display_email = request.form["email"]

    if request.form["is_artist"] == 't':
        is_artist = True
    else:
        is_artist = False  

    if request.form["show_unpaid"] == 't':
        show_unpaid = True
    else:
        show_unpaid = False  

    last_active = datetime.now()

    if request.form["link_to_website"]:
        link_to_website = request.form["link_to_website"]
    else:
        link_to_website = None

    if request.form["hourly_rate"]:
        hourly_rate = request.form["hourly_rate"]
    else:
        hourly_rate = None

    if request.form["phone"]:
        phone = request.form["phone"]
    else:
        phone = None

    if request.form["link_to_website"]:
        link_to_website = request.form["link_to_website"]
    else:
        link_to_website = None

    if request.form["bio"]:
        bio = request.form["bio"]
    else:
        bio = None

    if User.query.filter_by(email=email).one_or_none():
        flash(f"Welcome {user_name}. Please check {display_email} inbox for verification email.")
        return redirect("/")
    
    else:
        new_user = User(user_name=user_name, password=password, email=email,
            phone=phone, is_artist=is_artist,
            last_active=last_active, show_unpaid=show_unpaid, display_email=display_email,
            link_to_website=link_to_website, bio= bio, hourly_rate=hourly_rate)
        db.session.add(new_user)
        db.session.commit()
        flash(f"Welcome {user_name}. Please check {display_email} inbox for verification email.")
        return redirect("/")


@app.route('/profile')
@login_required
def user_profile():
    """Individual user profile, pertainable to logged in user."""

    email = current_user.display_email
    elist = []
    count = 100
    liame = email[::-1]   #It's email backwards.
    two_chars = []

    for c in liame:
        count += 1
        if c == '@':
            count = 0
        if count == 1 or count == 2:
            two_chars.append(c)

    elist.extend([ email[0], "*****", two_chars[1], two_chars[0] ])
    
    count = 0
    for c in email:
        if c == '@':
            count = 1
        if count == 1:
            elist.append(c)

        email = ''.join(elist)

    tags = Tag.query.all()


    return render_template("profile.html", email=email, tags=tags)


@app.route('/update_info', methods=['POST'])
def update_user_info():
    """Updates all user info, except e-mail and password. """

    if request.form["is_artist"] == 't':
        is_artist = True
    else:
        is_artist = False  

    current_user.is_artist = is_artist

    if request.form["show_unpaid"] == 't':
        show_unpaid = True
    else:
        show_unpaid = False  

    current_user.show_unpaid = show_unpaid

    new_tags_ids = request.form.getlist("tag")
    new_tags_list = []

    prev_tags = current_user.tags

    print(prev_tags)

    for tag in new_tags_ids:
        associated_tag = Tag.query.get(tag)
        new_tags_list.append(associated_tag)

    current_user.tags = new_tags_list

    db.session.commit()
    
    flash(f"Your information has been updated.")
    return redirect('/profile')


##################### Test Routes  vvvvvvvvvvvvvvv


@app.route('/calendar')
def show_calendar():
    """This is a page to test my calendar plug in."""

    return render_template("calendar_test.html")


@app.route('/savedate', methods=['POST'])
def save_date():
    """This is a TEST route to test my calendar plug in."""

    mydate = str(request.form["mydate"])

    flash(f"Date {mydate} selected.")


    posts = Post.query.all()
    posts.reverse()

    return render_template("posts.html", posts=posts)


##################### Test Routes Finished ^^^^^^^^^

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")