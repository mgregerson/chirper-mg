import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized

from forms import UserAddForm, LoginForm, MessageForm, CsrfForm, EditUserProfile
from models import db, connect_db, User, Message, LikedWarble

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)

connect_db(app)

##############################################################################
# User signup/login/logout

@app.before_request
def add_user_and_form_to_g():
    """If we're logged in, add curr user to Flask global.
    Adds CsrfForm to g whether user is logged in or not."""
    g.csrf = CsrfForm()

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def handle_signup():
    """Handle user signup.

    POST: Create new user and add to DB. Redirect to home page.

    GET: If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    do_logout()

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def handle_login():
    """Handle user login and redirect to homepage on success."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            form.username.data,
            form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.post('/logout')
def handle_logout():
    """Handle logout of user and redirect to homepage."""

    if g.csrf.validate_on_submit():
        flash('We are sorry to see you go!')
        do_logout()
        return redirect("/login")

    else:
        raise Unauthorized()

##############################################################################
# General user routes:

@app.get('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User
                                  .username
                                  .like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.get('/users/<int:user_id>')
def show_user(user_id):
    """Show user profile."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    return render_template('users/show.html', user=user)


@app.get('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.get('/users/<int:user_id>/followers')
def show_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.post('/users/follow/<int:follow_id>')
def start_following(follow_id):
    """Add a follow for the currently-logged-in user.

    Redirect to following page for the current for the current user.
    """
    # Validate on submit the CSRF form. The logout button is not executing the CSRF form without submit.
    if g.csrf.validate_on_submit():

        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")

        followed_user = User.query.get_or_404(follow_id)
        g.user.following.append(followed_user)
        db.session.commit()

        return redirect(f"/users/{g.user.id}/following")

    else:
        raise Unauthorized()


@app.post('/users/stop-following/<int:follow_id>')
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user.

    Redirect to following page for the current for the current user.
    """
    if g.csrf.validate_on_submit():

        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")

        followed_user = User.query.get(follow_id)
        g.user.following.remove(followed_user)
        db.session.commit()

        return redirect(f"/users/{g.user.id}/following")

    else:
        raise Unauthorized()



@app.route('/users/profile', methods=["GET", "POST"])
def update_profile():
    """GET: Render template for user to edit their profile.

       POST: Handle form, check that password is correct, and commit changes to the database. """
    if not g.user:
        raise Unauthorized()

    form = EditUserProfile(obj=g.user)

    if form.validate_on_submit():
        g.user.username = form.username.data
        g.user.email = form.email.data
        g.user.image_url = form.image_url.data
        g.user.header_image_url = form.header_image_url.data
        g.user.bio = form.bio.data
        password = form.password.data

        user = g.user.authenticate(g.user.username, password)

        if user:
            db.session.commit()
            return redirect(f"/users/{g.user.id}")
        else:
            form.password.errors = ["Invalid password."]
            return render_template("/users/edit.html", form=form)

    else:
        return render_template("/users/edit.html", form=form)


@app.post('/users/delete')
def delete_user():
    """Delete user.

    Redirect to signup page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    deleted_messages = Message.query.filter(Message.user_id == g.user.id).all()

    for message in deleted_messages:
        db.session.delete(message)

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")



##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def add_message():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/create.html', form=form)


@app.get('/messages/<int:message_id>')
def show_message(message_id):
    """Show a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get_or_404(message_id)
    return render_template('messages/show.html', message=msg)


@app.post('/messages/<int:message_id>/delete')
def delete_message(message_id):
    """Delete a message.

    Check that this message was written by the current user.
    Redirect to user page on success.
    """

    if g.csrf.validate_on_submit():

        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")

        msg = Message.query.get_or_404(message_id)
        db.session.delete(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    else:
        raise Unauthorized()


##############################################################################
# Liked Warbles Routes

@app.post('/messages/<int:message_id>/like')
def add_liked_warble(message_id):
    """Adds liked warble to the LikedWarble table. Redirects user back to the page that they were currently visiting."""

    origin_page = request.form['origin']

    if g.csrf.validate_on_submit() and not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")

    message = Message.query.get_or_404(message_id)

    if message.user_id == g.user.id:
        flash("You can't like your own warble, silly!")
        return redirect('/')

    liked_warble = LikedWarble(user_id = g.user.id, message_id=message.id)

    db.session.add(liked_warble)
    db.session.commit()

    return redirect(origin_page)

@app.post('/messages/<int:message_id>/unlike')
def remove_liked_warble(message_id):
    """Removes likedWarble instance and removes from the likedWarbles table. Redirects user to the page they were previously on"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    origin_page = request.form['origin']

    message = Message.query.get_or_404(message_id)

    liked_warble = LikedWarble.query.filter(g.user.id == LikedWarble.user_id,
                                             message.id == LikedWarble.message_id).first()

    db.session.delete(liked_warble)

    db.session.commit()

    return redirect(origin_page)

@app.get('/users/<int:user_id>/liked_messages')
def show_liked_warbles(user_id):
    """Displays user profile and a list of the users liked messages."""

    if g.csrf.validate_on_submit():
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get(user_id)

    return render_template('/users/liked_warbles.html', user=user)


##############################################################################
# Homepage and error pages


@app.get('/')
def display_homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """

    if g.user:

        followed_users = g.user.following
        followed_users.append(g.user)
        ids = [user.id for user in followed_users]

        messages = (Message
                    .query
                    .filter(Message.user_id.in_(ids))
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())

        return render_template('home.html', messages=messages)

    else:
        return render_template('home-anon.html')


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(response):
    """Add non-caching headers on every request."""

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
    response.cache_control.no_store = True
    return response
