from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sql
from sqlite3 import Error
import bcrypt

app = Flask(__name__)


def init_db():
    try:
        connection = sql.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users(
            email VARCHAR PRIMARY KEY,
            password VARCHAR
        );
    ''')
        connection.commit()
        connection.close()
    except Error as e:
        print(e)


# Call this when starting the application
init_db()


@app.route('/')
#renders login page when website is launched
def login():
    return render_template('index.html')


@app.route('/register')
#renders register page when register button clicked
def register():
    return render_template('register.html')


@app.route('/login', methods=['POST'])
#handles login logic
def login_post():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    #connect to db and make table if not already existing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users(
            email VARCHAR PRIMARY KEY,
            password VARCHAR
        );
    ''')
    #fetch email and passwords from webpage
    email = request.form.get('email')
    password = request.form.get('password')
    cursor.execute('SELECT password FROM Users WHERE email = ?', (email,))
    user = cursor.fetchone()
    connection.close()

    #Checks if email exits in Users table
    if user:
        hashed_pw = user[0]

        #checkpw function hashes inputted password with the same salt as the hashed password and sees if they match
        if bcrypt.checkpw(password.encode(), hashed_pw.encode()):
            return render_template('index.html', success="Successfully logged in!")
        else:
            return render_template('index.html', error="Incorrect password")
    else:
        return render_template('index.html', error="Incorrect email")


@app.route('/register', methods=['POST'])
#handles registration logic
def register_post():
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm-password')
    #fetches email and pass from form fields
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    #create table if it does not already exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users(
            email VARCHAR PRIMARY KEY,
            password VARCHAR
        );
    ''')

    #Check to make sure that email doesn't already exist in Database
    cursor.execute('SELECT * FROM Users WHERE email = ?', (email,))
    existing_user = cursor.fetchone()
    if existing_user: #email was found in the db
        connection.close()
        return render_template('register.html', error="Email already registered", email=email)

    if password != confirm_password: #passwords did not match
        return render_template('register.html', error="Passwords do not match", email=email)

    #hashes the password using bcrypt and then inserts the hashed value into the database
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cursor.execute('INSERT INTO Users (email, password) VALUES (?, ?);', (email, hashed_pw))
    connection.commit()
    connection.close()
    #returns successful message if registration is successful
    return render_template('register.html', success="Registration successful!")

'''
Helper code that displays contents of user table
@app.route('/query')
def query():
    try:
        conn = sql.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users')
        users = c.fetchall()
        conn.close()
        result = '<h2>Database Contents:</h2><ul>'
        for user in users:
            result += f'<li>ID: {user[0]}, Email: {user[1]}</li>'
        result += '</ul>'
        return result
    except Error as e:
        return f"Error: {str(e)}"
'''

if __name__ == '__main__':
    app.run(debug=True)