from flask import Flask, render_template, abort, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import SignUpForm, LoginForm, AddSong

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dfewfew123213rwdsgert34tgfd1234trgf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///songs.db'
db = SQLAlchemy(app)


# It creates a table called users with the columns id, username, and password.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)


# It creates a table called songs with the columns id, title, artist, year, genre, and user_id.
class Songs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    artist = db.Column(db.String(80), unique=False, nullable=False)
    year = db.Column(db.Integer, unique=False, nullable=False)
    genre = db.Column(db.String(80), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


db.create_all()


"""
    If the user is logged in, render the index.html template with the username and a message. If the
    user is not logged in, render the index.html template without the username and message.
    :return: the rendered template.
"""
@app.route('/', methods=['POST', 'GET'])
def index():
    # verify if user is logged in
    if 'username' in session:
        return render_template('index.html', username=session['username'], message='You are logged in!')
    return render_template('index.html')


"""
    If the form is submitted and the username and password are valid, then the user is logged in and
    redirected to the index page
    :return: The login page is being returned.
"""
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


"""
    If the form is valid, add the user to the database, and if the username already exists, return an
    error message.
    :return: a render_template object.
"""
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


"""
    It takes the username of the user who is logged in, and adds a song to the database.
    
    :param username: the username of the user who is logged in
    :return: the rendered template of the addsongs.html file.
"""
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


"""
    If the user is logged in, then render the playlist.html template with the songs that belong to the
    user
    
    :param username: The username of the user whose playlist you want to view
    :return: The user_id is being returned.
"""
@app.route('/playlist/<username>', methods=['POST', 'GET'])
def playlist(username):
    if 'user' in session:
        user_id = session['user']
        songs = Songs.query.filter_by(user_id=user_id).all()
        return render_template('playlist.html', songs=songs)
    return redirect(url_for('index'))


"""
    If the user is logged in, delete the song from the database and redirect to the playlist page.
    
    :param song_id: The id of the song to be deleted
    :return: the redirect function.
"""
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


"""
    If the user is logged in, then the song is queried by the song_id, the form is created, and if the
    form is validated, then the song is updated with the new data, and the user is redirected to the
    playlist page.
    
    :param song_id: the id of the song that is being edited
    :return: the rendered template of the edit.html page.
"""
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