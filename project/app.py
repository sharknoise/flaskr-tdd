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
SQLALCHEMY_DATABASE_URI = f'sqlite:///{Path(basedir).joinpath(DATABASE)}'
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
    """Searches the database for entries, displays them in reverse order."""
    entries = db.session.query(models.Post).order_by(models.Post.id.desc())
    return render_template('index.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    """Adds new post to the database."""
    if not session.get('logged_in'):
        abort(401)
    new_entry = models.Post(request.form['title'], request.form['text'])
    db.session.add(new_entry)
    db.session.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login/authentication/session management."""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """User logout/authentication/session management."""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))


@app.route('/delete/<int:post_id>', methods=['GET'])
def delete_entry(post_id):
    """Deletes post from database."""
    result = {'status': 0, 'message': 'Error'}
    try:
        db.session.query(models.Post).filter_by(id=post_id).delete()
        db.session.commit()
        result = {'status': 1, 'message': "Post Deleted"}
        flash('The entry was deleted.')
    except Exception as e:
        result = {'status': 0, 'message': repr(e)}
    return jsonify(result)


@app.route('/search/', methods=['GET'])
def search():
    query = request.args.get("query")
    entries = db.session.query(models.Post)
    if query:
        return render_template('search.html', entries=entries, query=query)
    return render_template('search.html')


if __name__ == "__main__":
    app.run()
