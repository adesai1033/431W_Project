from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3 as sql
from sqlite3 import Error
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session management


def init_db():
    try:
        connection = sql.connect('database.db')
        cursor = connection.cursor()
        # Create Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users(
            email VARCHAR PRIMARY KEY,
            password VARCHAR
        );
        ''')
        # Create Buyers table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Buyers(
            email VARCHAR PRIMARY KEY,
            first_name VARCHAR,
            last_name VARCHAR,
            address VARCHAR,
            credit_card VARCHAR,
            FOREIGN KEY (email) REFERENCES Users(email)
        );
        ''')
        # Create Sellers table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sellers(
            email VARCHAR PRIMARY KEY,
            business_name VARCHAR,
            business_phone VARCHAR,
            business_address VARCHAR,
            bank_info VARCHAR,
            FOREIGN KEY (email) REFERENCES Users(email)
        );
        ''')
        # Create Helpdesk table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Helpdesk(
            email VARCHAR PRIMARY KEY,
            employee_id VARCHAR,
            department VARCHAR,
            phone_ext VARCHAR,
            FOREIGN KEY (email) REFERENCES Users(email)
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

@app.route('/user_select')
def user_select():
    return render_template('user_select.html')

@app.route('/login', methods=['POST'])
#handles login logic
def login_post():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    #connect to db and make table if not already existing

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
    
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Users WHERE email = ?', (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        connection.close()
        return render_template('register.html', error="Email already registered", email=email)

    if password != confirm_password:
        return render_template('register.html', error="Passwords do not match", email=email)

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cursor.execute('INSERT INTO Users (email, password) VALUES (?, ?);', (email, hashed_pw))
    connection.commit()
    connection.close()
    
    # Store email in session for later use
    session['email'] = email
    return redirect(url_for('user_select'))

@app.route('/buyer_register', methods=['GET', 'POST'])
def buyer_register():
    if 'email' not in session:
        return redirect(url_for('register'))
        
    if request.method == 'GET':
        return render_template('buyer_reg.html')
    
    # Handle POST request
    email = session['email']  # Get email from session
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    address = request.form.get('address')
    credit_card = request.form.get('credit_card')

    connection = sql.connect('database.db')
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO Buyers (email, first_name, last_name, address, credit_card)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, first_name, last_name, address, credit_card))
        connection.commit()
        session.pop('email', None)  # Clear the session after successful registration
        return render_template('buyer_reg.html', success="Buyer registration successful!")
    except Error as e:
        return render_template('buyer_reg.html', error="Registration failed: " + str(e))
    finally:
        connection.close()

@app.route('/seller_register', methods=['GET', 'POST'])
def seller_register():
    if 'email' not in session:
        return redirect(url_for('register'))
        
    if request.method == 'GET':
        return render_template('seller_reg.html')
    
    # Handle POST request
    email = session['email']  # Get email from session
    business_name = request.form.get('business_name')
    business_phone = request.form.get('business_phone')
    business_address = request.form.get('business_address')
    bank_info = request.form.get('bank_info')

    connection = sql.connect('database.db')
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO Sellers (email, business_name, business_phone, business_address, bank_info)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, business_name, business_phone, business_address, bank_info))
        connection.commit()
        session.pop('email', None)  # Clear the session after successful registration
        return render_template('seller_reg.html', success="Seller registration successful!")
    except Error as e:
        return render_template('seller_reg.html', error="Registration failed: " + str(e))
    finally:
        connection.close()

@app.route('/helpdesk_register', methods=['GET', 'POST'])
def helpdesk_register():
    if 'email' not in session:
        return redirect(url_for('register'))
        
    if request.method == 'GET':
        return render_template('helpdesk_reg.html')
    
    # Handle POST request
    email = session['email']  # Get email from session
    employee_id = request.form.get('employee_id')
    department = request.form.get('department')
    phone_ext = request.form.get('phone_ext')

    connection = sql.connect('database.db')
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO Helpdesk (email, employee_id, department, phone_ext)
            VALUES (?, ?, ?, ?)
        ''', (email, employee_id, department, phone_ext))
        connection.commit()
        session.pop('email', None)  # Clear the session after successful registration
        return render_template('helpdesk_reg.html', success="Helpdesk registration successful!")
    except Error as e:
        return render_template('helpdesk_reg.html', error="Registration failed: " + str(e))
    finally:
        connection.close()

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