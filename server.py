from flask import Flask, render_template, request, jsonify, flash, redirect, session, abort, url_for
app=Flask(__name__)
from flask_bootstrap import Bootstrap
from jinja2 import StrictUndefined
from datetime import datetime, timedelta
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import json
import os
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Post, Zipcode, Tag
from random import randint
import boto3


login_manager = LoginManager()
login_manager.init_app(app)

app.secret_key = "thefriendswemadealongtheway"

app.jinja_env.undefined = StrictUndefined


## Change UPLOAD folder to our s3 bucket
UPLOAD_FOLDER = '/static/img'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
###############


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()
    ###Do I need to add more code here or is this complete?


@login_manager.unauthorized_handler
def unauthorized_callback():
    """If there is no user logged in,
    this will redirect the client back to the homepage."""
    flash("You will need to log in or create an account before viewing this page.")
    return render_template("homepage.html")


@app.errorhandler(404)
def page_not_found(e):
    """This is a custom 404 page."""

    flash("Error 404, page not found.")

    return render_template("homepage.html")


# @app.route('/bayjson.geojson')
# def serve_static():
#     with open('static/baysuburbs.geojson') as json_file:
#         data_one = json.load(json_file)
#     with open('static/sanjosesuburbs.geojson') as json_file:
#         data_two = json.load(json_file)


#     for locations in data_one["features"]:
#         if (locations["properties"])["zip"] == "94558":
#             data = locations

#     for locations in data_two["features"]:
#         if (locations["properties"])["ZCTA"] == "95123":
#             data = locations

#     return jsonify(data)

  

@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/artists')
@login_required
def display_artists():
    """Renders a page with all artists info."""

    artists = User.query.filter(User.is_artist==True, User.verified==True).order_by(User.last_active.desc())

    return render_template("artists.html", artists=artists)


@app.route('/users/<int:id>')
@login_required
def display_public_user(id):
    """Display user info if user is artist, or user is current_user"""

    page_user = User.query.get(id)

    if page_user == None:
        flash("Error, page not found.")
        return render_template("homepage.html")

    daysweek = list(current_user.daysweek)

    if page_user.is_artist or current_user.id == id:
        return render_template('user.html', user=page_user, daysweek=daysweek)
    else:
        flash("Error, page not found.")
        return render_template("homepage.html")


@app.route('/newpost')
@login_required
def new_post():
    """Renders a page with the option to post a new gig."""

    zipcode_instances = Zipcode.query.filter(Zipcode.location_name != 'Remote').all()

    zipcodes = []

    for zipcode in zipcode_instances:
        zipcodes.append(zipcode.valid_zipcode)

    locations = []

    for zipcode in zipcode_instances:
        locations.append(zipcode.location_name)



    locations = list(set(locations))

    locations.sort()

    locations.insert(0, "Remote")

    tags = Tag.query.all()

    def sort_tag_name(val):
        return val.tag_name

    tags.sort(key = sort_tag_name)


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
    user_id = current_user.id
    post_date = datetime.now()

    new_post = Post(post_title=post_title, description=description,
        zipcode=zipcode.valid_zipcode, creation_date=post_date, user_id=user_id)

    post_tags = request.form.getlist("tag")

    for tag in post_tags:
        associated_tag = Tag.query.get(tag)
        new_post.tags.append(associated_tag)

    db.session.add(new_post)

    db.session.commit()
        
    flash("Thank you. Your new post is now live.")

    return redirect("gigs")


@app.route('/gigs')
@login_required
def display_gigs():
    """Displays a list of all posts
    TODO: (Pinterest style ((AJAX? REACT??)) infinte scroll.
    Sort by most recent post at the top."""

    # overmorgen = datetime.now() + timedelta(days=2)
    # print(overmorgen)
    # print(type(overmorgen))

    # posts = Post.query.filter(Post.active == True).all()

    # for post in posts:
    #     if post.gig_date_end < overmorgen:
    #         post.active = False

    # db.session.commit()

    if current_user.show_unpaid == True:
        posts = Post.query.filter(Post.active == True).order_by(Post.creation_date.desc())
    else:
        posts = Post.query.filter(Post.active == True, Post.unpaid == False).order_by(Post.creation_date.desc())

    return render_template("gigs.html", posts=posts)


@app.route('/searchgigs', methods=['GET', 'POST'])
@login_required
def display_gig_results():
    """Basic string query gig search function"""

    search_string = request.form["search"]
    search_string = '%' + search_string + '%'

    posts = Post.query.filter(((Post.description.ilike(search_string)) | (Post.post_title.ilike(search_string))), Post.active == True).all()

    if posts == []:
        flash("No posting matched your search criteria.")

    return render_template("gigs.html", posts=posts)

@app.route('/advancedgigsearch')
@login_required
def advanced_search_gig_page():

    tags = Tag.query.all()

    def sort_tag_name(val):
        return val.tag_name

    tags.sort(key = sort_tag_name)

    locations = Zipcode.query.all()

    locations = list(set([i.region for i in locations]))

    locations.sort()

    locations.insert(0, "Location:")
    
    return render_template('advancedgigsearch.html', tags=tags, locations=locations)


@app.route('/searchgigsadvance', methods=['GET', 'POST'])
@login_required
def advanced_gigs_query():
    """This route process an advanced gig search."""

    if request.form.get("search", False):
        search_string = '%' + request.form["search"] + '%'
        s_posts = Post.query.filter(((Post.description.ilike(search_string)) | (Post.post_title.ilike(search_string))), Post.active == True).all()
    else:
        s_posts = Post.query.all()

    if request.form.get("tag", False):
        tags = request.form.getlist("tag")
        t_posts = []
        for tag in tags:
            tag_one = Tag.query.filter(Tag.tag_name == tag).one()
            t_posts.extend(tag_one.posts)
    else:
        t_posts = Post.query.all()

    if request.form["location"] != "Location:":
        location = request.form["location"]
        list_of_tuples = db.session.query(Zipcode,Post).join(Post).filter(Zipcode.region == location).all()
        l_posts = []
        for i in list_of_tuples:
            l_posts.append(i[1])
    else:
        l_posts = Post.query.all()

    venn_s_t = [a for a in s_posts for b in t_posts if a == b]

    posts = [c for c in venn_s_t for d in l_posts if c == d]

    return render_template("gigs.html", posts=posts)

@app.route('/gig/<int:post_id>')
def display_active_gig(post_id):
    """Displays a gig's page"""

    gig = Post.query.filter_by(post_id = post_id).one()

    data = None

    print(gig.zipcode)
    print(type(gig.zipcode))

    with open('static/baysuburbs.geojson') as json_file:
        data_one = json.load(json_file)
    with open('static/sanjosesuburbs.geojson') as json_file:
        data_two = json.load(json_file)

    for locations in data_one["features"]:
        if (locations["properties"])["zip"] == str(gig.zipcode):
            data = locations

    for locations in data_two["features"]:
        if (locations["properties"])["ZCTA"] == str(gig.zipcode):
            data = locations

    print(data)
    zipdata = data

    return render_template("gig.html", zipdata=zipdata)



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
    flashclass = 'class="alert alert-success success"'
    flash("You have successfully logged out.")

    return render_template("homepage.html", flashclass=flashclass)


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

    current_user.daysweek = new_avail

    db.session.commit()
    
    daysweek = list(new_avail)

    flash("You have successfully updated your availability.")

    return redirect('/availability')


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

    if request.form.get("link_to_website", False):
        link_to_website = request.form["link_to_website"]
    else:
        link_to_website = None

    if request.form.get("hourly_rate", False):
        hourly_rate = request.form["hourly_rate"]
    else:
        hourly_rate = None

    if request.form.get("phone", False):
        phone = request.form["phone"]
    else:
        phone = None

    if request.form.get("link_to_website", False):
        link_to_website = request.form["link_to_website"]
    else:
        link_to_website = None

    if request.form.get("bio", False):
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

@app.route('/changepic')
@login_required
def display_change_profile_picture():
    """Displays a form with a single option to upload a file"""

    return render_template("changepic.html")


@app.route('/uploadimg', methods=['POST'])
@login_required
def upload_image():
    """Handles uploading an image"""

    s3 = boto3.resource('s3')

    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    user = User.query.get(current_user.id)
    #implement Unique Here Storage Later

    if file.filename == '':
        flash('No selected file')
        return redirect('/changepic')

    if allowed_file(file.filename):

        num = randint(10000000, 99999999)

        file.filename = f'{current_user.email[0:4]}_profilepic_{num}'

        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print("###################FILENAME################")
        print(file.filename)

        user.img_route = file.filename

        db.session.commit()

    # s3.Bucket(os.environ.get('S3_BUCKET')).put_object(Key=file.filename, Body=file)

    s3.Bucket('bayart').put_object(Key=file.filename, Body=file)

    return redirect('/profile')


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


@app.route('/maptest')
def map_test():

    with open('static/baysuburbs.geojson') as json_file:
        data_one = json.load(json_file)
    with open('static/sanjosesuburbs.geojson') as json_file:
        data_two = json.load(json_file)

    for locations in data_one["features"]:
        if (locations["properties"])["zip"] == "94028":
            data = locations

    for locations in data_two["features"]:
        if (locations["properties"])["ZCTA"] == "94028":
            data = locations

    print(data)
    zipdata = data

    return render_template("maptest.html", zipdata=zipdata) 

##################### Test Routes Finished ^^^^^^^^^

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(host="0.0.0.0")