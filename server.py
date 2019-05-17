from flask import Flask, render_template, request, flash, redirect, session, abort, url_for
app=Flask(__name__)
from flask_bootstrap import Bootstrap
from jinja2 import StrictUndefined

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

@app.route('/homepage')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/logout')
@login_required
def logout():
    """Logs a user out and redirects to homepage."""

    # del session["user_id"]
    logout_user()
    flash("You have successfully logged out.")

    return redirect('/homepage')


@app.route('/login_form')
def present_login_form():
    """Displays the login form. Eventually I would incorporate this on the 
    homepage"""

    return render_template("login_form.html")



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

        return redirect('/homepage')
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


# @app.route('/register', methods=['POST'])
# def register_process():
#     """Process registration."""

#     # Get form variables

#     user_name = request.form["user_name"]
#     password = request.form["password"]
#     email = request.form["email"]
    
#     if (request.form["link_to_website"])
#         link_to_website = (request.form["link_to_website"])

#     zipcode = request.form["zipcode"]

#     if (request.form["hourly_rate"])
#         hourly_rate = (request.form["hourly_rate"])

#     new_user = User(user_name=user_name, password=password,
#                 email=email, zipcode=zipcode)

#     db.session.add(new_user)
#     db.session.commit()

#     flash(f"User {email} added.")
#     return redirect(f"/users/{new_user.user_name}")



# @app.route('/logout')
# @login_required
# def logout():
#     """Logs a user out."""
#     logout_user()
#     flash("You are now logged out.")
#     return redirect("homepage.html")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")