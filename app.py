# from flask import Flask, render_template, request, jsonify
# import mysql.connector

# app = Flask(__name__, template_folder='templates',static_folder='static')  # Ensure Flask serves HTML from templates

# # ✅ Home Route (Optional: Can remove if not needed)
# @app.route('/')
# def home():
#     return "Expense Tracker API is running!"

# def get_db_connection():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="arnikajain1174",  
#         database="user_db"
#     )

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         data = request.get_json()
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         query = """
#         INSERT INTO users (first_name, middle_name, last_name, email, username, password, gender, contact, security_key, city)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         values = (
#             data['first_name'], data['middle_name'], data['last_name'], 
#             data['email'], data['username'], data['password'], 
#             data['gender'], data['contact'], data['security_key'], data['city']
#         )

#         cursor.execute(query, values)
#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({"message": "User registered successfully!"})

#     return render_template('register.html')

# # ✅ Expense Submission API
# @app.route('/submit-expense', methods=['POST'])
# def submit_expense():
#     try:
#         data = request.json
#         category = data.get("category")
#         amount = data.get("amount")
#         mode = data.get("mode")
#         date = data.get("date")
#         description = data.get("description")

#         if not category or not amount or not mode or not date:
#             return jsonify({"error": "Missing required fields"}), 400

#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("""
#             INSERT INTO expenses (category, amount, mode, date, description) 
#             VALUES (%s, %s, %s, %s, %s)
#         """, (category, amount, mode, date, description))

#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({"message": "Expense added successfully!"}), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # ✅ Get All Expenses API
# @app.route('/get-expenses', methods=['GET'])
# def get_expenses():
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM expenses")
#         expenses = cursor.fetchall()
#         cursor.close()
#         conn.close()
#         return jsonify(expenses), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '_main_':
#     app.run(debug=True)

# @app.route('/submit', methods=['POST'])
# def submit():
#     email = request.form.get('email') or 'test@example.com'  # Replace with how you identify users (email or username)
    
#     # Capture the expense data from the form
#     budget = request.form.get('budget')
#     date = request.form.get('date')
#     payee = request.form.get('payee')
#     amount = request.form.get('amount')
#     amount_value = request.form.get('amount_value')
#     mode = request.form.get('mode')
#     category = request.form.get('category')

#     # Check if user exists
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
#     user = cursor.fetchone()
#     cursor.close()

#     if not user:
#         return redirect(url_for('register'))

#     # If user exists, process the form and save expense data
#     cursor = conn.cursor()
#     cursor.execute(
#         "INSERT INTO expenses (email, budget, date, payee, amount, amount_value, mode, category) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
#         (email, budget, date, payee, amount, amount_value, mode, category)
#     )
#     conn.commit()
#     cursor.close()
#     conn.close()

#     return render_template('index.html', message="Data submitted!")



from flask import Flask, render_template, request, redirect, session, send_file, url_for
import csv
import io
from fpdf import FPDF
from datetime import datetime, date 
import mysql.connector

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'  # Needed to use session


# MySQL connection config
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="arnikajain1174",  # Update if needed
        database="user_db"             # Your actual database name
    )

@app.route('/')
def home():
    return render_template('index.html')

# for home page
@app.route('/submit', methods=['POST'])
def submit():
    if 'user' not in session:
        return redirect(url_for('home', auth='required'))

    username = session['user']

    # Get form data
    budget = request.form.get('budget')
    date = request.form.get('date')
    payee = request.form.get('payee')
    transaction_type = request.form.get('transaction_type')
    amount = request.form.get('amount')
    payment_mode = request.form.get('payment_mode')
    category = request.form.get('category')

    # Save to DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO expenses (username, budget, date, payee, transaction_type, amount, payment_mode, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (username, budget, date, payee, transaction_type, amount, payment_mode, category)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('home', submitted='true'))


# for register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Capture the registration data from the form
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        gender = request.form.get('gender')
        contact = request.form.get('contact')
        security_key = request.form.get('security_key')
        city = request.form.get('city')

        # Insert the user data into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (first_name, middle_name, last_name, email, username, password, gender, contact, security_key, city) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (first_name, middle_name, last_name, email, username, password, gender, contact, security_key, city)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('home', register='success'))

    return render_template('register.html')


# for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        login_time = datetime.now()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if the user exists and password is correct in the `users` table
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            session['user'] = username

            # Log the successful login in the LOGIN table
            log_cursor = conn.cursor()
            log_cursor.execute("""
                INSERT INTO LOGIN (username, email, password, last_login, status)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE last_login = VALUES(last_login), status = 'Success'
            """, (username, user['email'], user['password'], login_time, 'Success'))
            conn.commit()

            log_cursor.close()
            cursor.close()
            conn.close()
            # return redirect(url_for('home', login='success'))
            return redirect(url_for('home') + '?login=success')


        else:
            # Log the failed login attempt
            log_cursor = conn.cursor()
            log_cursor.execute("""
                INSERT INTO LOGIN (username, email, password, last_login, status)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE last_login = VALUES(last_login), status = 'Failed'
            """, (username, '', password, login_time, 'Failed'))
            conn.commit()

            log_cursor.close()
            cursor.close()
            conn.close()
            return redirect(url_for('login', login='failed'))
        
    return render_template('login.html')

# for logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    # return redirect(url_for('home', logout='true'))
    return redirect(url_for('home') + '?logout=true')


# for history page
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('home', auth='required'))

    username = session['user']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT date, payee, transaction_type, amount, payment_mode, category, budget
        FROM expenses
        WHERE username = %s
        ORDER BY date DESC
    """, (username,))

    expenses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('history.html', expenses=expenses)


# for expense page
# @app.route("/expense", methods=["GET", "POST"])
# def expense():
#     if "user" not in session:
#         return redirect(url_for('home', auth='required'))

#     category_selected = None
#     expenses = []

#     if request.method == "POST":
#         category_selected = request.form.get("category")
#         username = session["user"]

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         query = """
#             SELECT * FROM expenses
#             WHERE username = %s AND category = %s
#         """
#         cursor.execute(query, (username, category_selected))
#         expenses = cursor.fetchall()

#         cursor.close()
#         conn.close()

#     return render_template("expense.html", expenses=expenses, category_selected=category_selected)

@app.route("/expense", methods=["GET", "POST"])
def expense():
    if "user" not in session:
        return redirect(url_for('home', auth='required'))

    category_selected = None
    expenses = []

    if request.method == "POST":
        category_selected = request.form.get("category")
        username = session["user"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT * FROM expenses
            WHERE username = %s AND category = %s AND transaction_type = 'expense'
        """
        cursor.execute(query, (username, category_selected))
        expenses = cursor.fetchall()

        cursor.close()
        conn.close()

    return render_template("expense.html", expenses=expenses, category_selected=category_selected)


# for report page
class DashboardPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Financial Dashboard Report', border=False, ln=True, align='C')
        self.ln(5)

    def summary_section(self, income, expense, balance):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.cell(60, 10, f'Total Income: Rs.{income:.2f}', 1, 0, 'C', fill=True)
        self.cell(60, 10, f'Total Expense: Rs.{expense:.2f}', 1, 0, 'C', fill=True)
        self.cell(60, 10, f'Net Balance: Rs.{balance:.2f}', 1, 1, 'C', fill=True)
        self.ln(10)

    def table_section(self, data):
        headers = ["Date", "Payee", "Type", "Amount", "Mode", "Category", "Budget"]
        col_widths = [25, 30, 25, 25, 30, 30, 25]

        self.set_font("Arial", 'B', 10)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, border=1, align='C')
        self.ln()

        self.set_font("Arial", "", 10)
        for row in data:
            self.cell(col_widths[0], 10, str(row['date']), border=1)
            self.cell(col_widths[1], 10, row['payee'], border=1)
            self.cell(col_widths[2], 10, row['transaction_type'], border=1)
            self.cell(col_widths[3], 10, f"{row['amount']:.2f}", border=1)
            self.cell(col_widths[4], 10, row['payment_mode'], border=1)
            self.cell(col_widths[5], 10, row['category'], border=1)
            self.cell(col_widths[6], 10, f"{row['budget']:.2f}", border=1)
            self.ln()

@app.route('/report', methods=['GET', 'POST'])
def report():
    if 'user' not in session:
        return redirect(url_for('home', auth='required'))

    if request.method == 'POST':
        start_date = request.form.get('start-date')
        end_date = request.form.get('end-date')
        action = request.form.get('action')  # 'csv' or 'pdf'
        username = session['user']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT date, payee, transaction_type, amount, payment_mode, category, budget
            FROM expenses
            WHERE username = %s AND date BETWEEN %s AND %s
            ORDER BY date DESC
        """, (username, start_date, end_date))
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        # CSV export
        if action == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Date', 'Payee', 'Type', 'Amount', 'Mode', 'Category', 'Budget'])
            for row in data:
                formatted_date = row['date'].strftime('%Y-%m-%d') if isinstance(row['date'], (datetime, date)) else str(row['date'])
                writer.writerow([
                    formatted_date,
                    row['payee'],
                    row['transaction_type'],
                    f"{row['amount']:.2f}",
                    row['payment_mode'],
                    row['category'],
                    f"{row['budget']:.2f}"
                ])

            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                download_name='expense_report.csv',
                as_attachment=True
            )

        # PDF export
        elif action == 'pdf':
            total_expense = sum(x['amount'] for x in data if x['transaction_type'] == 'Expense')
            total_income = sum(x['amount'] for x in data if x['transaction_type'] == 'Income')
            net_balance = total_income - total_expense

            pdf = DashboardPDF()
            pdf.add_page()
            pdf.summary_section(total_income, total_expense, net_balance)
            pdf.table_section(data)

            pdf_bytes = pdf.output(dest="S").encode("latin-1")
            return send_file(
                io.BytesIO(pdf_bytes),
                mimetype="application/pdf",
                download_name="financial_dashboard_report.pdf",
                as_attachment=True
            )

    return render_template("report.html")


# Route for Tips Page
@app.route('/tips')
def tips():
    return render_template('tips.html')

if __name__ == '__main__':
    app.run(debug=True)
