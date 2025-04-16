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
        if user_type == 'Buyer':
            return redirect(url_for('buyer_reg'))
        elif user_type == 'Seller':
            return redirect(url_for('seller_reg'))
        elif user_type == 'Helpdesk':
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
        return redirect(url_for('seller'))
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


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('add_product.html')

    # Handle POST request
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

    while 1 > 0:
        cursor.execute('SELECT * FROM Product_Listings WHERE Seller_Email = ? '
                       'and Listing_ID = ?',
                       (email, listingID,))
        existing = cursor.fetchone()
        if not existing:
            break
        else:
            listingID = random.randint(10000, 99999)
    cursor.execute('INSERT INTO Product_Listings (Seller_Email, Listing_ID,Category,'
                   'Product_Title,Product_Name,Product_Description,'
                   'Quantity,Product_Price,Status ) '
                   'VALUES (?,?,?,?,?,?,?,?,?);', (email, listingID, category,
                                                   product_title, product_name, description, quantity, price, 1))
    connection.commit()
    connection.close()
    return render_template('add_product.html', success="Product added successfully!")


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

#Rendering the Sellers currently listed products
@app.route('/seller', methods=['GET', 'POST'])
def seller():
    error = None
    email = session['email']
    result = get_seller_products(email)
    return render_template('sellers.html', error=error, result=result)

@app.route('/seller_reviews', methods=['GET', 'POST'])
def seller_reviews():
    error = None
    email = session['email']
    result = get_seller_reviews(email)
    overall_rating = get_seller_rating(email)
    return render_template('seller_view_reviews.html', error=error, result=result, overall_rating=overall_rating)

@app.route('/view_products')
def view_products():
    return redirect(url_for('seller'))

@app.route('/add_products')
def edit_products():
    return render_template('add_product.html')

@app.route('/view_ratings')
def view_ratings():
    return redirect(url_for('seller_reviews'))

@app.route('/add_category_request')
def add_category_request():
    return render_template('add_ctgry_req.html')


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
    return [cat[0] for cat in sub]


def edit_buyer_details(Buyer_Email, business_name, zipcode, street_num, street_name, credit_card_num, card_type, expire_month, expire_year,security_code):
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    query = """
    UPDATE Credit_cards
    SET  credit_card_num = ?, card_type = ?, expire_month = ?, expire_year = ?, security_code = ?,
    WHERE Owner_email = ?
    """
    cursor.execute(query, (credit_card_num, card_type, expire_month, expire_year, security_code, Buyer_Email))
    connection.commit()

    cursor.execute('SELECT buyer_address_id FROM Buyers WHERE email = ?', (Buyer_Email,))
    id = cursor.fetchone()[0]

    query = """
    UPDATE Addresses
    SET  zipcode = ?, street_num = ?, street_name = ?,
    WHERE address_id = ?
    """
    cursor.execute(query, (zipcode, street_num, street_name, id))
    connection.commit()

    query = """
    UPDATE Buyers
    SET  business_name = ?,
    WHERE email = ?
    """
    cursor.execute(query, (business_name, Buyer_Email))
    connection.commit()
    cursor.close()

def get_buyer_detail():
    email = session['email']
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    lst = [email]
    


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
        SELECT Product_Title, Product_Name, Product_Description, Quantity, Product_Price
        FROM Product_Listings 
        WHERE Seller_Email = ? AND Status = 1
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
    WHERE Seller_Email = ? AND Listing_ID = ?
    """

    cursor.execute(query, (Category, Product_Title, Product_Name, Product_Description, Quantity, Product_Price, Status, Seller_Email, Listing_ID,))
    connection.commit()
    connection.close()
    return

# Getting all seller reviews
def get_seller_reviews(email):
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    query = """
    SELECT r.Order_ID, r.Rate, r.Review_Desc
    FROM Reviews r, Orders o
    WHERE (r.Order_ID = o.Order_ID) AND o.Seller_Email = ?
    """

    cursor.execute(query, (email,))
    reviews = cursor.fetchall()
    connection.close()
    return reviews

# Calculates seller rating
def get_seller_rating(email):
    reviews = get_seller_reviews(email)

    if len(reviews) == 0:
        return None

    total = 0
    for r in reviews:
        total += r[1]

    return round(total / len(reviews), 1)


def get_pending_requests():
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    query = '''
            SELECT * 
            FROM Requests
            WHERE Status = 0
            '''

    cursor.execute(query)
    requests = cursor.fetchall()
    connection.close()
    return requests

def get_searchable_products(keyword):
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    query = '''
            SELECT Product_Title, Product_Name, Product_Description, Quantity, Product_Price
            FROM Product_Listings
            WHERE Product_Title LIKE ? OR Product_Description LIKE ? OR Category LIKE ? OR Seller_Email LIKE ?
            '''

    cursor.execute(query, (keyword,))
    products = cursor.fetchall()
    connection.close()
    return products

###buyer and category code beginning
@app.route('/buyers', methods=['GET', 'POST'])
def buyers():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        # Get root categories
        categories = getSubCategories("Root")
        return render_template('buyers.html', categories=categories, current_category=None)

    # Handle POST request for category selection
    selected_category = request.form.get('category')
    if selected_category:
        subcategories = getSubCategories(selected_category)
        parent = getParentCategory(selected_category)
        return render_template('buyers.html',
                               categories=subcategories,
                               current_category=selected_category,
                               parent_category=parent)

    return redirect(url_for('buyers'))


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


def getProductsByPriceRange(category_name, min_price=None, max_price=None):
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    query = """
        SELECT Product_Title, Product_Name, Product_Description, Quantity, Product_Price
        FROM Product_Listings 
        WHERE Category = ?
    """
    params = [category_name]

    if min_price is not None:
        query += " AND Product_Price >= ?"
        params.append(min_price)

    if max_price is not None:
        query += " AND Product_Price <= ?"
        params.append(max_price)

    query += " ORDER BY Product_Price"

    cursor.execute(query, params)
    products = cursor.fetchall()
    connection.close()

    return products

def getProductsByTitle(search=None):
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    query = """
            SELECT Product_Title, Product_Name, Product_Description, Quantity, Product_Price
            FROM Product_Listings 
            WHERE Product_Title LIKE ? OR Product_Name LIKE ?
            """
    search_pattern = f'%{search}%'
    params = [search_pattern, search_pattern]

    cursor.execute(query, params)
    products = cursor.fetchall()
    connection.close()

    return products

###buyer and category code ending



def getParentCategory(category_name):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    query = """
        SELECT parent_category
        FROM Categories
        WHERE category_name = ?;
    """
    cursor.execute(query, (category_name,))
    parent = cursor.fetchone()
    connection.close()
    return parent[0] if parent else None


@app.route('/getProducts', methods=['POST'])
def getProducts():
    selected_category = request.form['selected_category']
    final = [selected_category]
    subcategories = getSubCategories(selected_category)
    final += subcategories
    for i in subcategories:
        for k in getSubCategories(i):
            if k != []:
                final.append(k)
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    placeholders = ', '.join(['?'] * len(final))
    query = f"""
        SELECT DISTINCT * FROM Product_Listings
        WHERE category IN ({placeholders});
    """
    cursor.execute(query, final)
    rows = cursor.fetchall()
    connection.close()
    for i in range(len(rows)):
        rows[i] = list(rows[i])
    return rows

@app.route('/getProductsByPriceRange', methods=['POST'])
def getProductsByPriceRange():
    selected_category = request.form['selected_category']
    min_price = request.form.get('min_price', '')
    max_price = request.form.get('max_price', '')

    # Get all subcategories
    final = [selected_category]
    subcategories = getSubCategories(selected_category)
    final += subcategories
    for i in subcategories:
        for k in getSubCategories(i):
            if k != []:
                final.append(k)

    connection = sql.connect('database.db')
    cursor = connection.cursor()

    # Build the query based on whether min/max prices are provided
    placeholders = ', '.join(['?'] * len(final))
    query = f"""
        SELECT DISTINCT * FROM Product_Listings
        WHERE category IN ({placeholders})
    """
    params = final

    if min_price:
        query += " AND CAST(REPLACE(REPLACE(Product_Price, '$', ''), ',', '') AS DECIMAL) >= ?"
        params.append(min_price)
    if max_price:
        query += " AND CAST(REPLACE(REPLACE(Product_Price, '$', ''), ',', '') AS DECIMAL) <= ?"
        params.append(max_price)

    print("Query:", query)  # Debug print
    print("Params:", params)  # Debug print

    cursor.execute(query, params)
    rows = cursor.fetchall()
    connection.close()

    # Convert tuples to lists for JSON serialization
    return [list(row) for row in rows]


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