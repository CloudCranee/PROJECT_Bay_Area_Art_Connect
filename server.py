from flask import Flask, render_template, request, flash, redirect, session, abort
app=Flask(__name__)


from flask_login import LoginManager, UserMixin, login_user

from flask_sqlalchemy import SQLAlchemy

from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Post, Zipcode, Tag

login_manager = LoginManager()
login_manager.init_app(app)



app.secret_key = "secret"

# app.jinja_env.undefined = StrictUndefined

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


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

    if user:
        login_user(user)

        flash("You are now logged in.")

        next = request.args.get('next')
        
        if not is_safe_url(next):
            return abort(400)

        return redirect(next or flask.url_for('index'))
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