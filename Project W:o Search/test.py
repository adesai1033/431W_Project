import sqlite3 as sql
from sqlite3 import Error
from datetime import datetime

def getProducts():
    selected_category = "Electrical Supplies"
    final = [selected_category]
    subcategories = getSubCategories(selected_category)
    final+=subcategories
    for i in subcategories:
        for k in getSubCategories(i):
            if k!=[]:
                final.append(k)
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    placeholders = ', '.join(['?'] * len(final))
    query = f"""
        SELECT * FROM Product_Listings
        WHERE category IN ({placeholders});
    """
    cursor.execute(query, final)
    rows = cursor.fetchall()
    connection.close()
    for i in range(len(rows)):
        rows[i] = list(rows[i])
    return rows

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

def edit_buyer_info():
    email = 'o5mrsfw0@nittybiz.com'
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
    buyer_info = list(buyer_info)
    return buyer_info

def get_current_date():
    return datetime.now().strftime("%Y/%m/%d")\


def do():
    name = "Promotion"
    listing = 747
    name = name + "wow" + str(listing)
    return name
if __name__ == "__main__":
    print(do())
