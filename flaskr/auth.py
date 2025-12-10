import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

# creates a Blueprint named 'auth'. Like the application object, the blueprint needs to know where it’s defined, so __name__ is passed as the second argument. The url_prefix will be prepended to all the URLs associated with the blueprint.
bp = Blueprint('auth', __name__, url_prefix='/auth')
# The authentication blueprint will have views to register new users and to log in and log out. When the user visits the /auth/register URL, the register view will return HTML with a form for them to fill out. When they submit the form, it will validate their input and either show the form again with an error message or create the new user and go to the login page.

# @bp.route associates the URL /register with the register view function
@bp.route('/register', methods=('GET', 'POST'))
def register():
    # If the user submitted the form, request.method will be 'POST'. In this case, start validating the input.
    if request.method == 'POST':
        # the .form property is a special type of dict mapping submitted form, with keys and values
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # If username and password are not empty, insert the new user data into the database.
        if error is None:
            try:
                # The database library will take care of escaping the values so you are not vulnerable to a SQL injection attack.
                # For security, passwords should never be stored in the database directly. Instead, generate_password_hash() is used to securely hash the password, and that hash is stored.
                db.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, generate_password_hash(password)), )
                # Since this query modifies data, db.commit() needs to be called afterwards to save the changes.
                db.commit()
            # An sqlite3.IntegrityError will occur if the username already exists, which should be shown to the user as another validation error.
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                # After storing the user, they are redirected to the login page. url_for() generates the URL for the login view based on its name. This is preferable to writing the URL directly as it allows you to change the URL later without changing all code that links to it.
                return redirect(url_for("auth.login"))
        # If validation fails, the error is shown to the user. flash() stores messages that can be retrieved when rendering the template.
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)).fetchone()

        if user is None:
            error = 'Incorrect username.'
        # check_password_hash() hashes the submitted password in the same way as the stored hash and securely compares them
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # session is a dict that stores data across requests. When validation succeeds, the user’s id is stored in a new session. The data is stored in a cookie that is sent to the browser, and the browser then sends it back with subsequent requests. Flask securely signs the data so that it can’t be tampered with.
            session.clear()
            session['user_id'] = user['id']
            # Now that the user’s id is stored in the session, it will be available on subsequent requests. At the beginning of each request, if a user is logged in their information should be loaded and made available to other views.
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

# bp.before_app_request() registers a function that runs before the view function, no matter what URL is requested.
@bp.before_app_request
# load_logged_in_user checks if a user id is stored in the session and gets that user’s data from the database, storing it on g.user, which lasts for the length of the request.
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()

@bp.route('/logout')
# To log out, you need to remove the user id from the session. Then load_logged_in_user won’t load a user on subsequent requests.
def logout():
    session.clear()
    return redirect(url_for('index'))

# Require Authentication in Other Views
def login_required(view):
    # Creating, editing, and deleting blog posts will require a user to be logged in. A decorator can be used to check this for each view it’s applied to.
    @functools.wraps(view)
    # This decorator returns a new view function that wraps the original view it’s applied to. **kwargs allows you to pass a variable number of named arguments to a function
    def wrapped_view(**kwargs):
        # The wrapped_view function checks if a user is loaded and redirects to the login page otherwise.
        if g.user is None:
            return redirect(url_for('auth.login'))
        # If a user is loaded the original view is called and continues normally.
        return view(**kwargs)
    return wrapped_view

