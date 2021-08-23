from functools import wraps
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_sqlalchemy import SQLAlchemy

basedir = Path(__file__).resolve().parent
load_dotenv()

# configuration
DATABASE = "flaskr.db"
USERNAME = getenv('ADMIN_USERNAME')
PASSWORD = getenv('ADMIN_PASSWORD')
SECRET_KEY = getenv('SECRET_KEY')
# use sqlite when no env value is provided
SQLALCHEMY_DATABASE_URI = getenv(
    'DATABASE_URL',
    f'sqlite:///{Path(basedir).joinpath(DATABASE)}'
).replace("postgres://", "postgresql://", 1)
SQLALCHEMY_TRACK_MODIFICATIONS = False


# create and initialize a new Flask app
app = Flask(__name__)
# load the config
app.config.from_object(__name__)
# init sqlalchemy
db = SQLAlchemy(app)

from project import models  # noqa: E402


@app.route('/')
def index():
    """Search the database for entries, display them in reverse order."""
    entries = db.session.query(models.Post).order_by(models.Post.id.desc())
    return render_template('index.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    """Add a new post to the database."""
    if not session.get('logged_in'):
        abort(401)
    new_entry = models.Post(request.form['title'], request.form['text'])
    db.session.add(new_entry)
    db.session.commit()
    flash('New entry was successfully posted', 'success')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Manage user login/authentication/session."""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in.', 'success')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """Manage user logout/authentication/session."""
    session.pop('logged_in', None)
    flash('You were logged out.', 'success')
    return redirect(url_for('index'))


def login_required(f):
    """Decorate a route function to check if the user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Action unavailable for guests, please log in.', 'danger')
            return jsonify({'status': 0, 'message': 'Please log in.'}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.route('/delete/<int:post_id>', methods=['GET'])
@login_required
def delete_entry(post_id):
    """Delete an entry from the database."""
    result = {'status': 0, 'message': 'Error'}
    try:
        new_id = post_id
        db.session.query(models.Post).filter_by(id=new_id).delete()
        db.session.commit()
        result = {'status': 1, 'message': "Post Deleted"}
        flash('The entry was deleted.', 'success')
    except Exception as e:
        result = {'status': 0, 'message': repr(e)}
    return jsonify(result)


@app.route('/search/', methods=['GET'])
def search():
    """Search for entries in the database."""
    query = request.args.get("query")
    entries = db.session.query(models.Post)
    if query:
        return render_template('search.html', entries=entries, query=query)
    return render_template('search.html')


if __name__ == "__main__":
    app.run()
