from flask import Flask, render_template, request, jsonify, flash, redirect, session, abort, url_for
app=Flask(__name__)
from flask_bootstrap import Bootstrap
from jinja2 import StrictUndefined
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

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
    ###WHAT DO HERE ???



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

    users = User.query.all()

    artists = []

    for user in users:
        if user.is_artist == True:
            artists.append(user)

    return render_template("artists.html", artists=artists)


@app.route('/newpost')
@login_required
def new_post():
    """Renders a page with the option to post a new gig."""

    return render_template("new_post.html")


@app.route('/creategig', methods=['POST'])
def add_new_gig_to_database():
    """Adds a new gig to the database."""

    user_id = current_user.id
    
    post_title = request.form["post_title"]
    description = request.form["description"]
    zipcode = request.form["zipcode"]
    post_date = datetime.now()


    #CHECK IF THE ZIPCODE IS VALID USING AJAX/REACT/JS??
    #ON THE ACTUAL NEW POST PAGE

    new_post = Post(post_title=post_title, description=description,
        zipcode=zipcode, post_date=post_date)

    db.session.add(new_post)
    db.session.commit()
        
    flash("Thank you. Your new post is now live.")

    return redirect("posts")



@app.route('/logout')
@login_required
def logout():
    """Logs a user out and redirects to homepage."""

    # del session["user_id"]
    logout_user()
    flash("You have successfully logged out.")

    return redirect('/')


@app.route('/login_form')
def present_login_form():
    """Displays the login form. Eventually I would incorporate this on the 
    homepage"""

    return render_template("login_form.html")



@app.route('/posts')
@login_required
def display_posts():
    """Displays a list of all posts
    TODO: (Pinterest style ((AJAX? REACT??)) infinte scroll.
    Sort by most recent post at the top."""

    posts = Post.query.all()

    posts.reverse()

    return render_template("posts.html", posts=posts)




@app.route('/login', methods=['GET', 'POST'])
def login():
    """form to log in"""

    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user")
        return redirect("/login_form")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login_form")

    if user.is_authenticated:
        login_user(user)

        flash("You are now logged in.")

        next = request.args.get('next')
        
        # if not is_safe_url(next):
        #     return abort(400)

        return redirect('/')
    return render_template('login.html', form=form)


    # if not user:
    #     flash("No such user")
    #     return redirect("/login")
        
    # if user.password != password:
    #     flash("Incorrect password")
    #     return redirect("/login")

    # login_user(user)
    # flash("You are now logged in.")
    # return redirect(f"/users/{user.id}")




@app.route('/signup', methods=['GET'])
def register_form():
    """Show form for user signup."""

    return render_template("register_form.html")


@app.route('/availability', methods=['GET'])
@login_required
def display_availability_page():
    """Displays and artist's change availability page."""

    # User availabilty dates = current_user.id

    daysweek = list(current_user.daysweek)
    print(daysweek)


    return render_template("availability.html", daysweek=daysweek)



@app.route('/changeavailability', methods=['GET', 'POST'])
def change_availability():
    """Changes artist availability in database."""
    
    new_avail = request.form.get("dates")

    print(new_avail)

    current_user.daysweek = new_avail

    db.session.commit()
    
    daysweek = list(new_avail)

    flash("You have successfully updated your availability.")

    return render_template("availability.html", daysweek=daysweek)





@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables

    user_name = request.form["user_name"]
    password = request.form["password"]
    email = request.form["email"]
    isartist = request.form["isartist"]    
    link_to_website = request.form["link_to_website"]
    hourly_rate = request.form["hourly_rate"]
    phone = request.form["phone"]

    new_user = User(user_name=user_name, password=password,
                email=email, zipcode=zipcode, phone=phone)

    db.session.add(new_user)
    db.session.commit()

    flash(f"User {email} added.")
    return redirect(f"/users/{new_user.user_name}")


@app.route('/profile')
@login_required
def user_profile():
    """Individual user profile, pertainable to logged in user."""


    return render_template("profile.html")


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