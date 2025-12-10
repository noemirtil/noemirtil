import os
from flask import Flask


def create_app(test_config=None):
    # create the Flask instance
    # instance_relative_config=True tells the app that configuration files are relative to the instance folder. The instance folder is located outside the flaskr package and can hold local data that shouldn’t be committed to version control, such as configuration secrets and the database file.
    app = Flask(__name__, instance_relative_config=True)
    # set some default configuration that the app will use. SECRET_KEY is used by Flask and extensions to keep data safe. It’s set to 'dev' to provide a convenient value during development, but it should be overridden with a random value when deploying. DATABASE is the path where the SQLite database file will be saved. It’s under app.instance_path, which is the path that Flask has chosen for the instance folder
    app.config.from_mapping(
        SECRET_KEY="f9d15ab32178e46ad4ceba3ae439bc07566b2f844037368b4172ff3579a85bc9",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
        # .sqlite, .db and .db3 are common file extensions for SQLite databases and are functionally the same
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # app.config.from_pyfile() overrides the default configuration with values taken from the config.py file in the instance folder if it exists. For example, when deploying, this can be used to set a real SECRET_KEY.
        app.config.from_pyfile("config.py", silent=True)
    else:
        # test_config can also be passed to the factory, and in this case it will be used instead of the instance configuration. This is so the tests you’ll write later in the tutorial can be configured independently of any development values you have configured.
        app.config.from_mapping(test_config)

    try:
        # os.makedirs() ensures that app.instance_path exists. Flask doesn’t create the instance folder automatically, but it needs to be created because your project will create the SQLite database file there.
        os.makedirs(app.instance_path)
        # if another program is already using port 5000, you’ll see OSError when the server tries to start
    except OSError:
        pass

    # # a test page
    # @app.route("/hello")
    # def hello():
    #     return "Hello, World!"

    # import db.py and call its init_app()
    from . import db

    db.init_app(app)

    # import auth.py and register the blueprint using app.register_blueprint()
    from . import auth

    app.register_blueprint(auth.bp)

    # import blog.py and register the blueprint using app.register_blueprint()
    from . import blog

    app.register_blueprint(blog.bp)
    # Unlike the auth blueprint, the blog blueprint does not have a url_prefix. So the index view will be at /, the create view at /create, and so on. The blog is the main feature of Flaskr, so it makes sense that the blog index will be the main index. However, the endpoint for the index view defined below will be blog.index. Some of the authentication views referred to a plain index endpoint. app.add_url_rule() associates the endpoint name 'index' with the / url so that url_for('index') or url_for('blog.index') will both work, generating the same / URL either way.
    app.add_url_rule("/", endpoint="index")

    return app
