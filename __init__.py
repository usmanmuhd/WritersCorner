from functools import wraps
from flask import Flask, redirect, render_template, url_for, session, flash, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'hcjhvhi76546rfvjguttfgu6t'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogdata.sqlite3'

db = SQLAlchemy(app)
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    email = db.Column(db.String(100))
    def __init__(self, name, username, password, email):
        self.name = name
        self.username = username
        self.password = password
        self.email = email


class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    author = db.Column(db.Integer)
    content = db.Column(db.String(5000))
    def __init__(self, title, author, content):
        self.title = title
        self.author = author
        self.content = content


# A decorator for login_required for accessing pages
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Login Required to Access Page!')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# To make the session permanent
def session_persistence():
    session.permanent = True

# This page displays articles by all users
@app.route('/')
def index():
    content = Articles.query.all()
    return render_template('index.html', header="WritersCorner", articles=content[::-1])

# Login
@app.route('/login/', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        if 'username' not in session:
            return render_template('login.html', header='Login') # complete render_template
        else:
            return redirect(url_for('index'))
    if request.method == 'POST':
        attempted_username = request.form['username']
        attempted_password = request.form['password']
        user_data = Users.query.filter_by(username=attempted_username)
        if user_data.first():
            if attempted_password == user_data[0].password:
                session['username']=attempted_username
                if 'remember' in request.form:
                    session_persistence()
                flash("Logged In!")
                return redirect(url_for('index'))
        else:
            flash('Invalid Username or Password!')
            return redirect(url_for('login'))

# To display a particular article
@app.route('/<int:idd>/')
def article(idd):
    data = Articles.query.filter_by(id=idd).all()
    return render_template('article.html', header=data[0].title, aarticle=data)

# Logout is done
@app.route('/logout/')
@login_required
def logout():
    session.pop('username', None)
    session.permanent = False
    flash("Logged Out Sucessfully!")
    return redirect(url_for('index'))

# This should return user page that displays the articles written by a user
@app.route('/<user>/')
def user(user):
    data = Users.query.filter_by(username=user)
    if data.first():
        art = Articles.query.filter_by(author=user).all()
        return render_template('index.html', header=data.first().name, articles=art)
    else:
        flash('Wrong Username!')
        return redirect(url_for('index'))

# This if for signup
@app.route('/signup/', methods=['GET','POST'])
def sign_up():
    if request.method == 'GET':
        return render_template('signup.html', header='SignUp') # complete This
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        if not username or not email or not password or not name:
            flash('Please fill all the details!')
            return redirect(url_for('sign_up')) # Send back to signup page to complete details
        new_user = Users(name, username, password, email)
        db.session.add(new_user)
        db.session.commit()
        flash('User sucessfully Signed Up!')
        return redirect(url_for('index')) # make user sign in again to start

@app.route('/users/')
@login_required
def users():
    users = Users.query.all()
    return render_template('users.html', users=users, header='Users')

# To write a new article
@app.route('/new/', methods=['GET','POST'])
@login_required
def new():
    if request.method == 'POST':
        title = request.form['title']
        author = session['username']
        content = request.form['content']
        if not title or not content:
            flash('Please fill the all the details!')
            return redirect(url_for('new')) #back to the half filled form
        new_article = Articles(title, author, content)
        db.session.add(new_article)
        db.session.commit()
        flash('Article published sucessfully!')
        return redirect(url_for('article', idd=new_article.id)) # redirect to article
    if request.method == 'GET':
        return render_template('new.html', header='New Article') # send new article typing page

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
