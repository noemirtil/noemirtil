import sqlite3
from datetime import datetime
import click
from flask import current_app, g

def get_db():
    # g is a special object that is unique for each request. It is used to store data that might be accessed by multiple functions during the request. The connection is stored and reused instead of creating a new connection if get_db is called a second time in the same request.
    if 'db' not in g:
        # sqlite3.connect() establishes a connection to the file pointed at by the DATABASE configuration key.
        g.db =sqlite3.connect(
            # current_app is another special object that points to the Flask application handling the request. get_db will be called when the application has been created and is handling a request, so current_app can be used.
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # sqlite3.Row tells the connection to return rows that behave like dicts. This allows accessing the columns by name.
        g.db.row_factory = sqlite3.Row

    return g.db

# e refers to the error object passed to app.teardown_appcontext() in init_app, set to none by default
def close_db(e=None):
    # remove and retrieve a value associated with the key 'db' from the g object, which acts as a global object for the current application context. If 'db' is not present in g, it returns None instead of raising a KeyError.
    db = g.pop('db', None)

    # checks if a connection was created by checking if g.db was set. If the connection exists, it is closed.
    if db is not None:
        db.close()

def init_db():
    # get_db() returns a database connection, which is used to execute the commands read from schema.sql
    db = get_db()

    # open_resource() opens a file relative to the flaskr package, which is useful since you won’t necessarily know where that location is when deploying the application later
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# click.command() defines a command line command called init-db that calls the init_db() function and shows a success message to the user
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo('Initialized the database.')

# sqlite3.register_converter() tells Python how to interpret timestamp values in the database. We convert the value to a datetime.datetime.
sqlite3.register_converter("timestamp", lambda v: datetime.fromisoformat(v.decode()))

# The close_db and init_db_command functions need to be registered with the application instance; otherwise, they won’t be used by the application. However, since you’re using a factory function, that instance isn’t available when writing the functions. Instead, write a function that takes an application and does the registration.
def init_app(app):
    # app.teardown_appcontext() tells Flask to call that function when cleaning up after returning the response.
    app.teardown_appcontext(close_db)
    # app.cli.add_command() adds a new command that can be called with the flask command.
    app.cli.add_command(init_db_command)

