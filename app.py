from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'Hola Amigo',
    'password': 'Rishi@4273',
    'port': 3308
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG, database='employee_db')
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    try:
        # Create database if it doesn't exist
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS employee_db")
        conn.close()

        # Connect to the employee_db and create table
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) NOT NULL UNIQUE,
                position VARCHAR(100) NOT NULL,
                salary FLOAT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Database initialization error: {e}")
        return False

@app.route('/')
def index():
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return render_template('index.html', employees=[])
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()
        return render_template('index.html', employees=employees)
    except Error as e:
        flash(f'Error fetching employees: {str(e)}', 'error')
        return render_template('index.html', employees=[])
    finally:
        conn.close()

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'error')
            return redirect(url_for('index'))
        
        try:
            cursor = conn.cursor()
            sql = """INSERT INTO employees (name, email, position, salary)
                    VALUES (%s, %s, %s, %s)"""
            values = (
                request.form['name'],
                request.form['email'],
                request.form['position'],
                float(request.form['salary'])
            )
            cursor.execute(sql, values)
            conn.commit()
            flash('Employee added successfully!', 'success')
        except Error as e:
            conn.rollback()
            flash(f'Error adding employee: {str(e)}', 'error')
        finally:
            conn.close()
        return redirect(url_for('index'))
    
    return render_template('add_employee.html')

if __name__ == '__main__':
    if init_db():
        print("Database initialized successfully!")
        app.run(debug=True)
    else:
        print("Failed to initialize database. Please check your MySQL connection settings.")
