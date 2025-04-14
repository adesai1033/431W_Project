from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3 as sql
from sqlite3 import Error
import bcrypt
import random
import string

app = Flask(__name__)
app.secret_key = '1RnTEtT1YR'


def init_db():
    try:
        connection = sql.connect('database.db')
        cursor = connection.cursor()
        # Create Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users(
            email VARCHAR PRIMARY KEY,
            password VARCHAR
            ON DELETE CASCADE
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
# renders login page when website is launched
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
# renders register page when register button clicked
def register():
    return render_template('register.html')


@app.route('/user_select', methods=['GET', 'POST'])
def user_select():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        if user_type == 'buyer':
            return redirect(url_for('buyer_reg'))
        elif user_type == 'seller':
            return redirect(url_for('seller_reg'))
        elif user_type == 'helpdesk':
            return redirect(url_for('helpdesk_reg'))
        else:
            return render_template('user_select.html', error='Please select a valid user type')
    return render_template('user_select.html')

@app.route('/login_route')
def login_route():
    email = session.get('email')
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Buyers WHERE email = ?', (email,))
    result = cursor.fetchone()
    if result:
        return redirect(url_for('buyers'))
    cursor.execute('SELECT * FROM Sellers WHERE email = ?', (email,))
    result = cursor.fetchone()
    if result:
        return render_template('sellers.html')
    cursor.execute('SELECT * FROM Helpdesk WHERE email = ?', (email,))
    result = cursor.fetchone()
    if result:
        return render_template('helpdesk.html')
    return redirect(url_for('user_select'))

@app.route('/login', methods=['POST'])
# handles login logic
def login_post():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    # connect to db and make table if not already existing

    # fetch email and passwords from webpage
    email = request.form.get('email')
    password = request.form.get('password')
    cursor.execute('SELECT password FROM Users WHERE email = ?', (email,))
    user = cursor.fetchone()
    connection.close()

    # Checks if email exits in Users table
    if user:
        hashed_pw = user[0]

        # checkpw function hashes inputted password with the same salt as the hashed password and sees if they match
        if bcrypt.checkpw(password.encode(), hashed_pw.encode()):
            session['email'] = email
            return redirect(url_for('login_route'))
        else:
            return render_template('login.html', error="Incorrect password")
    else:
        return render_template('login.html', error="Incorrect email")


@app.route('/register', methods=['POST'])
# handles registration logic
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

@app.route('/add_product', methods=['POST'])
def add_product():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    listingID = random.randint(10000, 99999)
    product_title = request.form.get('product_title')
    description = request.form.get('description')
    category = request.form.get('category')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    product_name = request.form.get('product_name')
    email = session.get('email')

    while 1>0:
        cursor.execute('SELECT * FROM Product_Listings WHERE Seller_Email = ? '
                   'and Listing_ID = ?',
                   (email,listingID,))
        existing = cursor.fetchone()
        if not existing:
            break
        else:
            listingID = random.randint(10000, 99999)
    cursor.execute('INSERT INTO Product_Listings (Seller_Email, Listing_ID,Category,'
                   'Product_Title,Product_Name,Product_Description,'
                   'Quantity,Product_Price,Status ) '
                   'VALUES (?,?,?,?,?,?,?,?,?);', (email, listingID,category,
                    product_title,product_name,description,quantity,price,1))
    connection.commit()
    connection.close()
    return render_template('add_product.html')


@app.route('/buyer_reg', methods=['GET', 'POST'])
def buyer_reg():
    if 'email' not in session:
        return redirect(url_for('register'))

    if request.method == 'GET':
        return render_template('buyer_reg.html')

    # Handle POST request
    email = session['email']
    business_name = request.form.get('business_name')
    street_num = request.form.get('street_num')
    street_name = request.form.get('street_name')
    zipcode = request.form.get('zipcode')
    cc_num = request.form.get('cc_num')
    cc_type = request.form.get('cc_type')
    expire_month = request.form.get('expire_month')
    expire_year = request.form.get('expire_year')
    security_code = request.form.get('security_code')
    buyer_address_id = generate_unique_address_id()

    connection = sql.connect('database.db')
    cursor = connection.cursor()

    try:
        # Insert into Buyers table
        cursor.execute('''
            INSERT INTO Buyers (email, business_name, buyer_address_id)
            VALUES (?, ?, ?)
        ''', (email, business_name, buyer_address_id))

        # Insert into Address table
        cursor.execute('''
            INSERT INTO Address (address_id, zipcode, street_num, street_name)
            VALUES (?, ?, ?, ?)
        ''', (buyer_address_id, zipcode, street_num, street_name))

        # Insert into Credit Cards table
        cursor.execute('''
            INSERT INTO Credit_Cards (credit_card_num, card_type, expire_month, expire_year, security_code, Owner_email)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (cc_num, cc_type, expire_month, expire_year, security_code, email))

        connection.commit()
        return redirect(url_for('login_route'))
    except Error as e:
        return render_template('buyer_reg.html', error="Registration failed: " + str(e))
    finally:
        connection.close()


@app.route('/seller_reg', methods=['GET', 'POST'])
def seller_reg():
    if 'email' not in session:
        return redirect(url_for('register'))

    if request.method == 'GET':
        return render_template('seller_reg.html')

    # Handle POST request
    email = session['email']  # Get email from session
    business_name = request.form.get('business_name')
    street_num = request.form.get('street_num')
    street_name = request.form.get('street_name')
    zipcode = request.form.get('zipcode')
    bank_routing_number = request.form.get('bank_routing_number')
    bank_account_number = request.form.get('bank_account_number')
    balance = request.form.get('balance')
    business_address_id = generate_unique_address_id()

    connection = sql.connect('database.db')
    cursor = connection.cursor()

    try:
        # Insert into Sellers table
        cursor.execute('''
            INSERT INTO Sellers (email, business_name, Business_Address_ID, bank_routing_number, bank_account_number, balance)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (email, business_name, business_address_id, bank_routing_number, bank_account_number, balance))

        # Insert into Address table
        cursor.execute('''
            INSERT INTO Address (address_id, zipcode, street_num, street_name)
            VALUES (?, ?, ?, ?)
        ''', (business_address_id, zipcode, street_num, street_name))

        connection.commit()
        return redirect(url_for('login_route'))
    except Error as e:
        return render_template('seller_reg.html', error="Registration failed: " + str(e))
    finally:
        connection.close()

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))


@app.route('/helpdesk_reg', methods=['GET', 'POST'])
def helpdesk_reg():
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
        return redirect(url_for('login_route'))
    except Error as e:
        return render_template('helpdesk_reg.html', error="Registration failed: " + str(e))
    finally:
        connection.close()

#@app.route('/buyers')
#def buyers():
  #top_categories = topLevelCategories()
    #return render_template("buyers.html", categories=top_categories)

def getProducts():
    selected_category = request.form['selected_category']
    subcategories = getSubCategories(selected_category)


def getSubCategories(parent_category):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    query = """
        SELECT category_name
    FROM Categories
    WHERE parent_category = ?;
    """
    cursor.execute(query, (parent_category,))
    sub = cursor.fetchall()
    connection.close()
    lst = []
    for i in sub:
        lst+=list(i)
    return lst

def topLevelCategories():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    query = """
        SELECT category_name
    FROM Categories
    WHERE parent_category = 'Root';
    """
    cursor.execute(query)
    toplevel = cursor.fetchall()
    connection.close()
    lst = []
    for i in toplevel:
        lst+=list(i)
    return lst


# Generates a unique address ID
def generate_unique_address_id():
    while True:
        address_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        connection = sql.connect('database.db')
        cursor = connection.cursor()

        query = f"SELECT EXISTS(SELECT 1 FROM Address WHERE address_id = ?)"
        cursor.execute(query, (address_id,))

        exists = cursor.fetchone()[0]

        if not exists:
            connection.close()
            break

    return address_id

# Gets a seller's active products
def get_seller_products(email):
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    query = """
        SELECT *
        FROM Product_Listings 
        WHERE Seller_Email = ? AND Status = 1)
               """

    cursor.execute(query, (email,))
    products = cursor.fetchall()

    return products

# Function for a seller to edit their information
def edit_product_details(Seller_Email, Listing_ID, Category, Product_Title, Product_Name, Product_Description, Quantity, Product_Price, Status):
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    query = """
    UPDATE Product_Listings
    SET  Category = ?, Product_Title = ?, Product_Name = ?, Product_Description = ?, Quantity = ?, Product_Price = ?, Status = ?
    WHERE Seller_Email = ? AND Listing_ID = ?)
    """

    cursor.execute(query, (Category, Product_Title, Product_Name, Product_Description, Quantity, Product_Price, Status, Seller_Email, Listing_ID,))

    return

# Getting all seller reviews
def get_seller_feedback(email):
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    query = """
    SELECT r.Order_ID, r.Rate, r.Review_Desc
    FROM Reviews r, Orders o
    WHERE (r.Order_ID = o.Order_ID) AND o.Seller_Email = ?
    """

    cursor.execute(query, (email,))
    reviews = cursor.fetchall()

    return reviews

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

@app.route('/view-products')
def view_products():
    return render_template('view_products.html')

@app.route('/edit-products')
def edit_products():
    return render_template('edit_products.html')

@app.route('/view-ratings')
def view_ratings():
    return render_template('view_ratings.html')

###buyer and category code beginning
@app.route('/buyers')
def buyers():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    
    # Get all categories and their relationships
    cursor.execute('''
        SELECT parent_category, category_name
        FROM Categories
        ORDER BY parent_category, category_name
    ''')
    categories = cursor.fetchall()
    connection.close()
    
    # Build category tree recursively
    def build_category_tree(parent_name):
        children = []
        for parent, name in categories:
            if parent == parent_name:
                child = {
                    'name': name,
                    'children': build_category_tree(name)
                }
                children.append(child)
        return children
    
    # Start with root categories
    category_tree = build_category_tree('Root')
    
    return render_template('buyers.html', root_categories=category_tree)

@app.route('/category/<category_name>')
def view_category_products(category_name):
    if 'email' not in session:
        return redirect(url_for('login'))
    
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    
    # Get products in this category
    cursor.execute('''
        SELECT * FROM Product_Listings 
        WHERE Category = ?
    ''', (category_name,))
    products = cursor.fetchall()
    
    # Get subcategories
    cursor.execute('''
        SELECT category_name FROM Categories 
        WHERE parent_category = ?
    ''', (category_name,))
    subcategories = cursor.fetchall()
    
    connection.close()
    
    return render_template('category_products.html', 
                         category_name=category_name,
                         products=products,
                         subcategories=subcategories)

###buyer and category code ending


if __name__ == '__main__':
    app.run(debug=True)