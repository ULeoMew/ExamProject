# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, request, url_for, g
from flask_login import LoginManager, login_user , logout_user , current_user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
DEBUG = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.sqlite"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self): 
        return True

    def get_id(self): 
        return str(self.id)
        
    def __repr__(self):
        return self.username

class Entries(db.Model):
    __tablename__ = "entries"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    text = db.Column(db.Text)

    def __init__(self, username, text):
        self.username = username
        self.text = text
        
@app.route("/")
def index():
    return render_template("index.html")

@app.errorhandler(404)
def pageNotFound(error):
    return render_template("404.html"), 404

@app.route("/about")
def about():
    return render_template("aboutProject.html")

@app.route("/whatfirst")
def whatfirst():
    return render_template("whatfirst.html")

@app.route("/komunikacii")
def komunikacii():
    return render_template("komunikacii.html")

@app.route("/interior")
def interior():
    return render_template("interior.html")

@app.route("/catalog")
def catalog():
    return render_template("catalog.html")

@app.route("/club", methods=['GET', 'POST'])
def club():
    username = None
    if request.method == 'POST':
        username = request.form['username']
        text = request.form['text']
        if text == '':
            note = "Пустий коментар"
            return render_template("club.html", note=note)
        else:
            new_comment = Entries(username=username, text=text)
            db.session.add(new_comment)                         
            db.session.commit()
    rows = Entries.query.all()                              
    return render_template("club.html", entries=rows, username=username)

@app.route('/newuser', methods=['GET', 'POST'])
def add_user():
    if request.method == 'GET':
        return render_template('new_user.html', note=None)
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if username == '' or password == '' or '@' not in email:
            return render_template('new_user.html', note='Перевірте коректність імейлу. Перевірте чи всі поля заповнені.')
        isRegistered = User.query.filter_by(email=email).first()
        if isRegistered != None:            
            return render_template('new_user.html', note='Дані введені неповністю або вже закріплені за іншим користувачем')

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

@app.route('/l', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html", mistake=None)
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        registered_user = User.query.filter_by(username=username, email=email, password=password).first()
        if registered_user != None:
            login_user(registered_user) 
            return redirect(url_for('club'))
        else:
            return render_template("login.html", mistake="Помилка в імені користувача, імейлі або паролі.")
        
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_manager.user_loader   
def load_user(id):
    return User.query.get(int(id))

@app.before_request     
def before_request():
    g.user = current_user

if __name__ == "__main__":
    app.run()