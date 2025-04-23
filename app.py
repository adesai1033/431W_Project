from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3 as sql
from sqlite3 import Error
import bcrypt
import random
import string
from datetime import datetime

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
        return redirect(url_for('helpdesk'))
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
        return render_template('helpdesk.html')

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


def edit_buyer_details(Buyer_Email, business_name, zipcode, street_num, street_name,
                       credit_card_num, card_type, expire_month, expire_year, security_code):
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    query = """
    UPDATE Credit_cards
    SET credit_card_num = ?, card_type = ?, expire_month = ?, expire_year = ?, security_code = ?
    WHERE Owner_email = ?
    """
    cursor.execute(query, (credit_card_num, card_type, expire_month, expire_year, security_code, Buyer_Email))
    connection.commit()

    cursor.execute('SELECT buyer_address_id FROM Buyers WHERE email = ?', (Buyer_Email,))
    address_id_row = cursor.fetchone()
    address_id = address_id_row[0]

    query = """
    UPDATE Address
    SET zipcode = ?, street_num = ?, street_name = ?
    WHERE address_id = ?
    """
    cursor.execute(query, (zipcode, street_num, street_name, address_id))
    connection.commit()

    query = """
    UPDATE Buyers
    SET business_name = ?
    WHERE email = ?
    """
    cursor.execute(query, (business_name, Buyer_Email))
    connection.commit()

    cursor.close()
    connection.close()


@app.route('/get_buyer_info', methods=['GET', 'POST'])
def get_buyer_info():
    email = session['email']

    if request.method == 'POST':
        business_name = request.form['business_name']
        zipcode = request.form['zipcode']
        street_num = request.form['street_num']
        street_name = request.form['street_name']
        credit_card_num = request.form['credit_card_num']
        card_type = request.form['card_type']
        expire_month = request.form['expire_month']
        expire_year = request.form['expire_year']
        security_code = request.form['security_code']

        edit_buyer_details(email, business_name, zipcode, street_num, street_name,
                           credit_card_num, card_type, expire_month, expire_year, security_code)

    connection = sql.connect('database.db')
    cursor = connection.cursor()
    query = '''
        SELECT
            b.business_name,
            a.zipcode,
            a.street_num,
            a.street_name,
            c.credit_card_num,
            c.card_type,
            c.expire_month,
            c.expire_year,
            c.security_code
        FROM Buyers b
        JOIN Address a ON b.buyer_address_id = a.address_id
        JOIN Credit_Cards c ON b.email = c.Owner_email
        WHERE b.email = ?
    '''
    cursor.execute(query, (email,))
    buyer_info = cursor.fetchone()
    connection.close()

    return render_template('edit_buyer_details.html', info=buyer_info)

def get_buyer_orders(email):
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    query = """
            SELECT o.Order_ID, pl.Product_Name, o.Seller_Email, o.Date
            FROM Orders o, Product_Listings pl
            WHERE o.Buyer_Email = ? AND o.Listing_ID = pl.Listing_ID and o.Order_ID NOT IN (SELECT Order_ID
            FROM Buyers b           )
            
            """
    cursor.execute(query, (email,))
    orders = cursor.fetchall()
    connection.close()
    return orders

def submit_new_review(order_id, rate, desc):
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    query = "INSERT INTO Reviews (Order_ID, Rate, Review_Desc) VALUES (?, ?, ?)"

    cursor.execute(query, (order_id, rate, desc))
    connection.commit()
    connection.close()

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
        SELECT Seller_Email, Listing_ID, Category, Product_Title, Product_Name, Product_Description, Quantity, Product_Price
        FROM Product_Listings 
        WHERE Seller_Email = ? AND Status = 1
               """

    cursor.execute(query, (email,))
    products = cursor.fetchall()
    connection.close()
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

@app.route('/edit_product', methods=['POST'])
def edit_product():
    Seller_Email = request.form['Seller_Email']
    Listing_ID = request.form['Listing_ID']
    Product_Title = request.form['Product_Title']
    Product_Name = request.form['Product_Name']
    Product_Description = request.form['Product_Description']
    Quantity = request.form['Quantity']
    Product_Price = request.form['Product_Price']
    Category = request.form['Category']
    Status = 1

    edit_product_details(Seller_Email, Listing_ID, Category, Product_Title, Product_Name, Product_Description, Quantity, Product_Price, Status)

    return redirect(url_for('seller'))

@app.route('/delete_product', methods=['POST'])
def delete_product():
    Seller_Email = request.form['Seller_Email']
    Listing_ID = request.form['Listing_ID']
    Product_Title = request.form['Product_Title']
    Product_Name = request.form['Product_Name']
    Product_Description = request.form['Product_Description']
    Quantity = request.form['Quantity']
    Product_Price = request.form['Product_Price']
    Category = request.form['Category']
    Status = 0

    edit_product_details(Seller_Email, Listing_ID, Category, Product_Title, Product_Name, Product_Description, Quantity, Product_Price, Status)

    return redirect(url_for('seller'))

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
            FROM Request
            WHERE request_status = 0
            '''

    cursor.execute(query)
    requests = cursor.fetchall()
    connection.close()
    lst = []
    for i in requests:
        lst.append(list(i))
    return lst

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

@app.route('/buyer_order_history')
def buyer_order_history():
    email = session.get('email')
    result = get_buyer_orders(email)
    return render_template('buyer_order_history.html', result=result)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    order_id = request.form['Order_ID']
    rate = int(request.form['rating'])
    desc = request.form['reviewText']

    submit_new_review(order_id, rate, desc)
    return redirect(url_for('buyer_order_history'))


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
    
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    
    final = [selected_category]
    subcategories = getSubCategories(selected_category)
    final += subcategories
    for i in subcategories:
        for k in getSubCategories(i):
            if k != []:
                final.append(k)
    
    placeholders = ', '.join(['?'] * len(final))
    query = f"""
        SELECT DISTINCT * FROM Product_Listings
        WHERE Category IN ({placeholders})
    """
    cursor.execute(query, final)
    products = cursor.fetchall()
    connection.close()
    
    return render_template('category_products.html',
                         category_name=selected_category,
                         products=products)

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
        WHERE Category IN ({placeholders})
    """
    params = final

    if min_price:
        query += " AND CAST(REPLACE(REPLACE(Product_Price, '$', ''), ',', '') AS DECIMAL) >= ?"
        params.append(min_price)
    if max_price:
        query += " AND CAST(REPLACE(REPLACE(Product_Price, '$', ''), ',', '') AS DECIMAL) <= ?"
        params.append(max_price)

    cursor.execute(query, params)
    products = cursor.fetchall()
    connection.close()

    return render_template('category_products.html',
                         category_name=selected_category,
                         products=products)


def get_current_date():
    return datetime.now().strftime("%Y/%m/%d")

@app.route('/helpdesk', methods=['GET', 'POST'])
def helpdesk():
    result = get_pending_requests()
    return render_template('helpdesk.html',result = result)


@app.route('/helpdesk_app')
def helpdesk_app():
    return render_template('helpdesk_app.html')


@app.route('/submit_helpdesk_app', methods=['POST'])
def submit_helpdesk_app():
    email = request.form.get('email')
    password = request.form.get('password')
    application_text = request.form.get('application_text')

    # Hash the password
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    connection = sql.connect('database.db')
    cursor = connection.cursor()

    try:
        # Check if email already exists
        cursor.execute('SELECT * FROM Users WHERE email = ?', (email,))
        if cursor.fetchone():
            return render_template('helpdesk_app.html', error="Email already registered")

        # Create helpdesk_applications table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS helpdesk_applications (
                email VARCHAR PRIMARY KEY,
                password VARCHAR,
                FOREIGN KEY (email) REFERENCES Users(email)
            )
        ''')

        # Insert into helpdesk_applications table
        cursor.execute('INSERT INTO helpdesk_applications (email, password) VALUES (?, ?)', (email, hashed_pw))

        # Find helpdesk staff with least pending requests
        cursor.execute('''
            SELECT h.email, COUNT(r.request_id) as pending_count
            FROM Helpdesk h
            LEFT JOIN Request r ON h.email = r.helpdesk_staff_email AND r.request_status = 1
            GROUP BY h.email
            ORDER BY pending_count ASC
            LIMIT 1
        ''')
        assigned_staff = cursor.fetchone()
        assigned_email = assigned_staff[0] if assigned_staff else None

        # Generate a unique 3-digit request ID
        request_id = random.randint(100, 999)
        while True:
            cursor.execute('SELECT * FROM Request WHERE request_id = ?', (request_id,))
            if not cursor.fetchone():
                break
            request_id = random.randint(100, 999)

        # Insert into Request table
        cursor.execute('''
            INSERT INTO Request (request_id, sender_email, helpdesk_staff_email, request_type, request_desc, request_status)
            VALUES (?, ?, ?, 'APP', ?, 0)
        ''', (request_id, email, assigned_email, application_text))

        connection.commit()
        return render_template('helpdesk_app.html', success="Application submitted successfully!")
    except Error as e:
        return render_template('helpdesk_app.html', error="Error submitting application: " + str(e))
    finally:
        connection.close()


@app.route('/purchase', methods=['POST'])
def purchase():
    if 'email' not in session:
        return redirect(url_for('login'))

    listing_id = request.form.get('listing_id')
    quantity = int(request.form.get('quantity'))
    category = request.form.get('category')

    connection = sql.connect('database.db')
    cursor = connection.cursor()

    try:
        # Get product details
        cursor.execute('SELECT Product_Title, Product_Price, Seller_Email FROM Product_Listings WHERE Listing_ID = ?',
                       (listing_id,))
        product = cursor.fetchone()
        if not product:
            return redirect(url_for('buyers'))

        product_title, price_str, seller_email = product

        # Clean the price string and convert to float
        price = float(price_str.replace('$', '').strip())

        # Calculate total payment
        total_payment = price * quantity

        # Store order details in session for checkout
        session['pending_order'] = {
            'listing_id': listing_id,
            'quantity': quantity,
            'category': category,
            'product_title': product_title,
            'price': price,
            'seller_email': seller_email,
            'total_payment': total_payment
        }

        return redirect(url_for('secure_checkout'))

    except Error as e:
        return redirect(url_for('buyers'))
    except ValueError as e:
        return redirect(url_for('buyers'))
    finally:
        connection.close()


@app.route('/secure_checkout', methods=['GET', 'POST'])
def secure_checkout():
    if 'email' not in session or 'pending_order' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        order = session['pending_order']
        payment_info = getPaymentInfo()
        return render_template('secure_checkout.html',
                               order=order,
                               buyer_email=session['email'],
                               payment_info=payment_info)

    order = session['pending_order']
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    try:
        cursor.execute('SELECT Quantity FROM Product_Listings WHERE Listing_ID = ?', (order['listing_id'],))
        current_quantity = cursor.fetchone()[0]

        if order['quantity'] > current_quantity:
            return render_template('secure_checkout.html',
                                   order=order,
                                   buyer_email=session['email'],
                                   error='Not enough stock available')

        order_id = random.randint(100000, 999999)
        while True:
            cursor.execute('SELECT * FROM Orders WHERE Order_ID = ?', (order_id,))
            if not cursor.fetchone():
                break
            order_id = random.randint(100000, 999999)

        new_quantity = current_quantity - order['quantity']
        if new_quantity == 0:
            cursor.execute(
                'UPDATE Product_Listings SET Quantity = ?, Status = ? WHERE Seller_Email = ? AND Listing_ID = ?',
                (0, 2, order['seller_email'], order['listing_id']))
        else:
            cursor.execute('UPDATE Product_Listings SET Quantity = ? WHERE Listing_ID = ?',
                           (new_quantity, order['listing_id']))
        connection.commit()

        # Insert into Orders table
        cursor.execute('''
            INSERT INTO Orders (Order_ID, Seller_Email, Listing_ID, Buyer_Email, Date, Quantity, Payment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, order['seller_email'], order['listing_id'], session['email'],
              get_current_date(), order['quantity'], order['total_payment']))
        connection.commit()

        # Update seller's balance
        cursor.execute('SELECT balance FROM Sellers WHERE email = ?', (order['seller_email'],))
        result = cursor.fetchone()[0]
        result += order['total_payment']
        cursor.execute('UPDATE Sellers SET balance = ? WHERE email = ?', (result, order['seller_email'],))
        connection.commit()

        session.pop('pending_order', None)  # Clear pending order
        return redirect(url_for('buyer_order_history'))

    except Error as e:
        connection.rollback()
        return render_template('secure_checkout.html',
                               order=order,
                               buyer_email=session['email'],
                               error='Error processing order: ' + str(e))
    finally:
        connection.close()


def getPaymentInfo():
    email = session.get('email')
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Credit_Cards WHERE Owner_email = ?', (email,))
    result = cursor.fetchall()
    lst = []
    for i in result:
        for k in i:
            lst.append(k)
    return lst
'''
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    listing_id = request.form['listing_id']
    seller_email = request.form['seller_email']
    price = request.form['price']
    quantity = int(request.form['quantity'])
    buyer_email = session.get('email')
    payment = price * quantity
    order_id = random.randint(100000, 999999)
    order_date = get_current_date()
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute(
        INSERT INTO orders (Order_ID, Seller_Email, Listing_ID, Buyer_Email, Date, Quantity, Payment)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    , (order_id, seller_email, listing_id, buyer_email, order_date, quantity, payment))
    connection.commit()

    cursor.execute('SELECT balance FROM Sellers WHERE email = ?', (seller_email,))
    result = cursor.fetchone()[0]
    result+=payment
    cursor.execute('UPDATE Sellers SET balance = ? WHERE email = ?', (result, seller_email,))
    connection.commit()

    cursor.execute('SELECT Quantity FROM Product_Listings WHERE Seller_Email = ? AND Listing_ID = ?', (seller_email,listing_id,))
    result = cursor.fetchone()[0]
    if result == quantity:
        cursor.execute('UPDATE Product_Listings SET Quantity = ?, Status = ? WHERE email = ? AND Listing_ID = ?', (0,2, seller_email,listing_id,))
    else:
        result-=quantity
        cursor.execute('UPDATE Product_Listings SET Quantity = ? WHERE email = ? AND Listing_ID = ?', (result, seller_email,listing_id,))
    connection.commit()
    connection.close()
    return redirect(url_for('buyers'))


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

@app.route('/search_products', methods=['POST'])
def search_products():
    if 'email' not in session:
        return redirect(url_for('login'))

    search_term = request.form.get('search', '').lower()
    category = request.form.get('category', '')

    connection = sql.connect('database.db')
    cursor = connection.cursor()

    try:
        # If a category is selected, search within that category
        if category and category != 'None':
            final = [category]
            subcategories = getSubCategories(category)
            final += subcategories
            for i in subcategories:
                for k in getSubCategories(i):
                    if k != []:
                        final.append(k)

            placeholders = ', '.join(['?'] * len(final))
            query = f"""
                SELECT DISTINCT * FROM Product_Listings
                WHERE Category IN ({placeholders})
                AND LOWER(Product_Title) LIKE ?
            """
            params = final + [f'%{search_term}%']
        else:
            # Search across all products
            query = """
                SELECT DISTINCT * FROM Product_Listings
                WHERE LOWER(Product_Title) LIKE ?
            """
            params = [f'%{search_term}%']

        print(f"Executing query: {query} with params: {params}")  # Debug print
        cursor.execute(query, params)
        products = cursor.fetchall()
        print(f"Found {len(products)} products")  # Debug print

        return render_template('category_products.html',
                             category_name=category if category and category != 'None' else 'Search Results',
                             products=products)

    except Error as e:
        print(f"Error in search: {str(e)}")  # Debug print
        return redirect(url_for('buyers'))
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)