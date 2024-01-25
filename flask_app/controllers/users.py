from flask import render_template, request, redirect, url_for, session, flash
from flask_app.models.user import User

from flask_app import app

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)     # we are creating an object called bcrypt, which is made by invoking the function Bcrypt with our app as an argument


# home page with forms
@app.route("/")
def index():
    return render_template("index.html")

# CREATE
# "Add User"
@app.route('/users/register', methods=['POST'])
def add_user():
    # We call the staticmethod on User model to validate
    if not User.validate_user(request.form):
    # redirect to the route where the user form is rendered.
        return redirect('/')
    
    print(request.form['pwd'])
    # create the hash
    pw_hash = bcrypt.generate_password_hash(request.form['pwd'])
    print(pw_hash)
    # put the pw_hash into the data dictionary
    data = {
        # shortcut to get all info from request.form
        **request.form,
        "pwd" : pw_hash
    }
    # Call the CREATE add @classmethod on User
    user_id = User.add(data)
    # store user id into session
    session['user_id'] = user_id

    return redirect(url_for('get_one'))

# READ/GET method, one record
@app.route("/dashboard")
def get_one():
    # protection - prevent access w/o login
    if 'user_id' not in session:
        return redirect('/')
    else:
    # elif 'user_id' in session:
        user_id = session['user_id']
    
    data = {
        'user_id' : user_id
    }

    # calling the get_one method and supplying it with the id of the user we want to get
    current_user = User.get_one(data)
    # passing one user to our template so we can display them
    return render_template("dashboard.html", one_user = current_user)

# VALIDATE
@app.route('/users/login', methods=['POST'])
def login():
    # # See staticmethod - validate_login() in user.py
    # # We call the staticmethod on User model to validate
    # if not User.validate_login(request.form):
    # # redirect to the route where the user form is
    #     return redirect('/')

    # email check
    data = {
        'email' : request.form['email']
    }

    user_in_db = User.get_one_by_email(data)

    if not user_in_db:
        flash("Invalid email or password", 'login')
        return redirect('/')

    # password check
    if not bcrypt.check_password_hash(user_in_db.password, request.form['pwd']):
        flash("Invalid email or password", 'login')
        return redirect('/')

    session['user_id'] = user_in_db.id
    print('function ran')
    return redirect('/dashboard')

@app.route('/logout')
def destroy_session():
    session.clear()
    return redirect('/')