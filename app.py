import re
from flask import Flask, render_template, abort, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import SignUpForm, LoginForm, AddSong
from decouple import config as config_decouple

db = SQLAlchemy()

def create_app(environment):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dfewfew123213rwdsgert34tgfd1234trgf'
    app.config.from_object(environment)

    with app.app_context():
        db.init_app(app)
        db.create_all()

    return app

enviroment = config['development']
if config_decouple('PRODUCTION', default=False):
    enviroment = config['production']

app = create_app(enviroment)


# Users Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)


# Songs Model
class Songs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    artist = db.Column(db.String(80), unique=False, nullable=False)
    year = db.Column(db.Integer, unique=False, nullable=False)
    genre = db.Column(db.String(80), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


db.create_all()


@app.route('/', methods=['POST', 'GET'])
def index():
    # verify if user is logged in
    if 'username' in session:
        return render_template('index.html', username=session['username'], message='You are logged in!')
    return render_template('index.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['username'] = form.username.data
        user = User.query.filter_by(username = form.username.data, password = form.password.data).first()
        if user is None:
            return render_template('login.html', form=form, message='Invalid username or password')
        else:
            session['user'] = user.id
            return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('index'))


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        mew_user = User(username=form.username.data, password=form.password.data)
        db.session.add(mew_user)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            return render_template('signup.html', form=form, error="Username already exists")
        finally:
            db.session.close()
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route('/addsongs/<username>', methods=['POST', 'GET'])
def addSongs(username):
    form = AddSong()
    if form.validate_on_submit():
        new_song = Songs(title=form.title.data, artist=form.artist.data, year=form.year.data, genre=form.genre.data, user_id=session['user'])
        db.session.add(new_song)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            return render_template('addsongs.html', form=form, error="Song already exists")
        finally:
            db.session.close()
        return redirect(url_for('playlist', username=username))
    return render_template('addsongs.html', form=form)

@app.route('/playlist/<username>', methods=['POST', 'GET'])
def playlist(username):
    if 'user' in session:
        user_id = session['user']
        songs = Songs.query.filter_by(user_id=user_id).all()
        return render_template('playlist.html', songs=songs)
    return redirect(url_for('index'))


@app.route('/delete/<song_id>', methods=['POST', 'GET'])
def delete(song_id):
    if 'user' in session:
        song = Songs.query.filter_by(id=song_id).first()
        db.session.delete(song)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            return render_template('delete.html', error="Song doesn't exist")
        finally:
            db.session.close()
        return redirect(url_for('playlist', username=session['username']))
    return redirect(url_for('index'))


@app.route('/edit/<song_id>', methods=['POST', 'GET'])
def edit(song_id):
    if 'user' in session:
        song = Songs.query.filter_by(id=song_id).first()
        form = AddSong()
        if form.validate_on_submit():
            song.title = form.title.data
            song.artist = form.artist.data
            song.year = form.year.data
            song.genre = form.genre.data
            db.session.commit()
            return redirect(url_for('playlist', username=session['username']))
        return render_template('edit.html', form=form, song=song)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, load_dotenv=True)
