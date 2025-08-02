# app.py
from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
DATABASE = 'grocery.db'

# Initialize database
def init_db():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        address TEXT
                    )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS admins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT
                    )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        price REAL,
                        image TEXT
                    )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        product_name TEXT,
                        price REAL,
                        address TEXT
                    )''')
        cur.execute("INSERT OR IGNORE INTO admins (username, password) VALUES (?, ?)", ("admin", "admin123"))
        con.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        address = request.form['address']
        with sqlite3.connect(DATABASE) as con:
            try:
                con.execute("INSERT INTO users (username, password, address) VALUES (?, ?, ?)", (uname, pwd, address))
                con.commit()
                return redirect('/login')
            except:
                return "Username already exists"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        with sqlite3.connect(DATABASE) as con:
            user = con.execute("SELECT * FROM users WHERE username=? AND password=?", (uname, pwd)).fetchone()
            if user:
                session['user'] = uname
                return redirect('/products')
            else:
                return "Invalid credentials"
    return render_template('login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        with sqlite3.connect(DATABASE) as con:
            admin = con.execute("SELECT * FROM admins WHERE username=? AND password=?", (uname, pwd)).fetchone()
            if admin:
                session['admin'] = uname
                return redirect('/admin_dashboard')
            else:
                return "Invalid admin credentials"
    return render_template('admin_login.html')

@app.route('/products')
def products():
    if 'user' in session:
        with sqlite3.connect(DATABASE) as con:
            products = con.execute("SELECT * FROM products").fetchall()
        return render_template('products.html', products=products)
    return redirect('/login')

@app.route('/place_order/<int:product_id>')
def place_order(product_id):
    if 'user' in session:
        with sqlite3.connect(DATABASE) as con:
            product = con.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
            user = con.execute("SELECT address FROM users WHERE username=?", (session['user'],)).fetchone()
            con.execute("INSERT INTO orders (username, product_name, price, address) VALUES (?, ?, ?, ?)",
                        (session['user'], product[1], product[2], user[0]))
            con.commit()
        return redirect('/order_success')
    return redirect('/login')

@app.route('/order_success')
def order_success():
    return render_template('order_success.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' in session:
        with sqlite3.connect(DATABASE) as con:
            products = con.execute("SELECT * FROM products").fetchall()
        return render_template('admin_dashboard.html', products=products)
    return redirect('/admin_login')

@app.route('/add_product', methods=['POST'])
def add_product():
    if 'admin' in session:
        name = request.form['name']
        price = request.form['price']
        image = request.form['image']
        with sqlite3.connect(DATABASE) as con:
            con.execute("INSERT INTO products (name, price, image) VALUES (?, ?, ?)", (name, price, image))
            con.commit()
        return redirect('/admin_dashboard')
    return redirect('/admin_login')

@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    if 'admin' in session:
        with sqlite3.connect(DATABASE) as con:
            con.execute("DELETE FROM products WHERE id=?", (product_id,))
            con.commit()
        return redirect('/admin_dashboard')
    return redirect('/admin_login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
