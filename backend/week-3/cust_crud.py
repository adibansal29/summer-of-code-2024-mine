from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import psycopg2
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
import bcrypt

app = Flask(__name__)

# conn = psycopg2.connect("dbname=DSOC user=postgres password=Ab290805")
# cur = conn.cursor()
# cur.execute(''' alter table Staff add column is_approved boolean''')
# cur.execute(''' alter table Staff add column s_password varchar(100)''')
# cur.execute(''' alter table Customer add column c_password varchar(100)''')

app.secret_key = '12d'
def db_connection():
    conn = psycopg2.connect("dbname=DSOC user=postgres password=Ab290805")
    return conn


#Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, email, password, role, is_admin = False, pseudo_admin = False):
        self.id = id
        self.email = email
        self.password = password
        self.role = role
        self.is_admin = is_admin
        self.pseudo_admin = pseudo_admin


@login_manager.user_loader
def load_user(user_id):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Staff WHERE s_ID = %s", (user_id,))
    staff = cur.fetchone()
    if staff:
        return User(id=staff[0], email=staff[2], password=staff[6],is_admin = staff[3], pseudo_admin = staff[5], role='staff')
    
    cur.execute("SELECT * FROM Customer WHERE c_ID = %s", (user_id,))
    customer = cur.fetchone()
    if customer:
        return User(id=customer[0], email=customer[2], password=customer[4], role='customer')
    
    return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (not current_user.is_admin and not current_user.pseudo_admin):
            flash('You do not have permission to access this resource.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'staff':
            flash('You do not have permission to access this resource.', 'danger')
            return redirect(url_for('retrieve_customer'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def hello():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        # password = request.form['password']
        password = request.form['password'].encode('utf-8')
        role = request.form['role']
        
        conn = db_connection()
        cur = conn.cursor()
        
        if role == 'staff':
            cur.execute("SELECT * FROM Staff WHERE s_email = %s", (email,))
            staff = cur.fetchone()
            # if staff and staff[6] == password:
            if staff and bcrypt.checkpw(password, staff[6].encode('utf-8')):
                user = User(id=staff[0], email=staff[2], password=staff[6], role='staff', is_admin=staff[3], pseudo_admin=staff[5])
                login_user(user)
                flash('Logged in successfully as Staff.', 'success')
                return render_template('index.html')
        
        elif role == 'customer':
            cur.execute("SELECT * FROM Customer WHERE c_email = %s", (email,))
            customer = cur.fetchone()
            # if customer and customer[4] == password:
            if customer and bcrypt.checkpw(password, customer[4].encode('utf-8')):
                user = User(id=customer[0], email=customer[2], password=customer[4], role='customer')
                login_user(user)
                flash('Logged in successfully as Customer.', 'success')
                return redirect(url_for('retrieve_customer'))
        
        flash('Invalid credentials or role. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))



@app.route("/index/")
@login_required
@staff_required
def index():
    return render_template('index.html')






#staff CRUD Operations
@app.route("/staff/create/", methods=['GET','POST'])
@login_required
@admin_required
def create_staff():
    if request.method == 'POST':
        s_ID = request.form['s_ID']
        s_name = request.form['s_name']
        s_email = request.form['s_email']
        s_contact = request.form['s_contact']
        s_isAdmin = request.form['s_isAdmin']
        is_approved = request.form['is_approved']
        s_password = request.form['s_password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(s_password, bcrypt.gensalt()).decode('utf-8')
        conn = db_connection()
        cur = conn.cursor()
        cur.execute(''' insert into Staff values (%s, %s, %s, %s, %s, %s, %s)'''
                    ,(s_ID, s_name, s_email, s_isAdmin, s_contact, is_approved, hashed_password,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Staff created successfully!', 'success')
        return redirect(url_for('retrieve_staff'))
    return render_template('create_staff.html')



@app.route("/staff/retrieve/", defaults={'s_ID': None})
@app.route("/staff/<s_ID>/")
@login_required
@staff_required
def retrieve_staff(s_ID):
    conn = db_connection()
    cur = conn.cursor()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 's_ID')
    sort_order = request.args.get('sort_order', 'asc')

    if s_ID:
        cur.execute('''select * from Staff where s_ID = %s''', (s_ID,))
        staff = cur.fetchone()

    else:
        query = f"select * from Staff where s_ID ilike %s order by {sort_by} {sort_order} limit %s offset %s"
        cur.execute(query, (f'%{search_query}%', per_page, (page-1)*per_page,))
        staff = cur.fetchall()

    cur.execute('''select count(*) from Staff where s_ID ilike %s''', (f'%{search_query}%',))
    total_staff = cur.fetchone()[0]
    cur.close()
    conn.close()
    return render_template('retrieve_staff.html', staff_list=staff, page=page, per_page=per_page, total_items=total_staff, search_query=search_query, sort_by=sort_by, sort_order=sort_order)


@app.route("/staff/update/<s_ID>/", methods = ['GET','POST'])
@login_required
@admin_required
def update_staff(s_ID):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute('''select * from Staff where s_ID = %s''', (s_ID,))
    staff = cur.fetchone()
    cur.close()
    conn.close()

    if request.method == 'POST':
        s_ID2 = request.form['s_ID']
        s_name = request.form['s_name']
        s_email = request.form['s_email']
        s_contact = request.form['s_contact']
        s_isAdmin = request.form['s_isAdmin']
        is_approved = request.form['is_approved']
        s_password = request.form['s_password']
        if s_password:
            s_password = s_password.encode('utf-8')
            hashed_password = bcrypt.hashpw(s_password, bcrypt.gensalt()).decode('utf-8')
        else:
            hashed_password = staff[6]
        conn = db_connection()
        cur = conn.cursor()
        cur.execute('''update Staff set s_ID = %s, s_name = %s, s_email = %s, s_contact = %s, s_isAdmin = %s, is_approved = %s, s_password = %s where s_ID = %s''',
                    (s_ID2, s_name, s_email, s_contact, s_isAdmin, is_approved, hashed_password, s_ID,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Staff updated successfully!', 'success')
        return redirect(url_for('retrieve_staff'))
    return render_template('update_staff.html', staff = staff)


@app.route("/staff/delete/<s_ID>/", methods = ['POST'])
@login_required
@admin_required
def delete_staff(s_ID):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute('''delete from Staff where s_ID = %s returning *''', (s_ID,))
    del_item = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    flash(f'Staff deleted successfully! {del_item}', 'success')
    return redirect(url_for('retrieve_staff'))




#customer CRUD Operations
@app.route("/customer/create/", methods=['GET','POST'])
def create_customer():
    if request.method == 'POST':
        c_ID = request.form['c_ID']
        c_name = request.form['c_name']
        c_email = request.form['c_email']
        c_contact = request.form['c_contact']
        c_password = request.form['c_password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(c_password, bcrypt.gensalt()).decode('utf-8')
        conn = db_connection()
        cur = conn.cursor()
        cur.execute(''' insert into Customer values (%s, %s, %s, %s, %s)'''
                    ,(c_ID, c_name, c_email, c_contact, hashed_password,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Customer created successfully!', 'success')
        return redirect(url_for('retrieve_customer'))
    return render_template('create_customer.html')


@app.route("/customer/retrieve/", defaults={'c_ID': None})
@app.route("/customer/<c_ID>/")
@login_required
def retrieve_customer(c_ID):
    conn = db_connection()
    cur = conn.cursor()
    if current_user.role == 'customer':
        # Retrieve only the logged-in customer's details
        cur.execute('''SELECT * FROM Customer WHERE c_ID = %s''', (current_user.id,))
        customer = cur.fetchone()
        cur.close()
        conn.close()
        return render_template('retrieve_customer.html', customer_list=[customer], page=1, per_page=1, total_items=1)


    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'c_ID')
    sort_order = request.args.get('sort_order', 'asc')

    if c_ID:
        cur.execute('''select * from Customer where c_ID = %s''', (c_ID,))
        customer = cur.fetchone()

    else:
        query = f"select * from Customer where c_ID ilike %s order by {sort_by} {sort_order} limit %s offset %s"
        cur.execute(query, (f'%{search_query}%', per_page, (page-1)*per_page,))
        customer = cur.fetchall()

    cur.execute('''select count(*) from Customer where c_ID ilike %s''', (f'%{search_query}%',))
    total_customer = cur.fetchone()[0]
    cur.close()
    conn.close()
    return render_template('retrieve_customer.html', customer_list=customer, page=page, per_page=per_page, total_items=total_customer, search_query=search_query, sort_by=sort_by, sort_order=sort_order)


@app.route("/customer/update/<c_ID>/", methods = ['GET','POST'])
@login_required
def update_customer(c_ID):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute('''select * from Customer where c_ID = %s''', (c_ID,))
    customer = cur.fetchone()
    cur.close()
    conn.close()

    if request.method == 'POST':
        c_ID2 = request.form['c_ID']
        c_name = request.form['c_name']
        c_email = request.form['c_email']
        c_contact = request.form['c_contact']
        c_password = request.form['c_password']
        if c_password:
            c_password = c_password.encode('utf-8')
            hashed_password = bcrypt.hashpw(c_password, bcrypt.gensalt()).decode('utf-8')
        else:
            hashed_password = customer[4]
        conn = db_connection()
        cur = conn.cursor()
        cur.execute('''update Customer set c_ID = %s, c_name = %s, c_email = %s, c_contact = %s, c_password = %s where c_ID = %s''',
                    (c_ID2, c_name, c_email, c_contact, hashed_password, c_ID,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('retrieve_customer'))
    return render_template('update_customer.html', customer = customer)


@app.route("/customer/delete/<c_ID>/", methods = ['POST'])
@login_required
def delete_customer(c_ID):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute('''delete from Customer where c_ID = %s returning *''', (c_ID,))
    del_item = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    flash(f'Customer deleted successfully! {del_item}', 'success')
    return redirect(url_for('retrieve_customer'))




#Transaction CRUD
@app.route("/transaction/create/", methods=['GET','POST'])
@login_required
@staff_required
def create_transaction():
    if request.method == 'POST':
        t_ID = request.form['t_ID']
        c_ID = request.form['c_ID']
        s_ID = current_user.id
        t_date = request.form['t_date']
        t_amount = request.form['t_amount']
        t_desc = request.form['t_category']
        conn = db_connection()
        cur = conn.cursor()
        cur.execute(''' insert into Transaction values (%s, %s, %s, %s, %s, %s)'''
                    ,(t_ID, c_ID, s_ID, t_date, t_amount, t_desc,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Transaction created successfully!', 'success')
        return redirect(url_for('retrieve_transaction'))
    return render_template('create_transaction.html')


@app.route("/transaction/retrieve/")
@login_required
@staff_required
def retrieve_transaction():
    conn = db_connection()
    cur = conn.cursor()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 't_ID')
    sort_order = request.args.get('sort_order', 'asc')


    
    query = f"select * from Transaction where t_ID ilike %s order by {sort_by} {sort_order} limit %s offset %s"
    cur.execute(query, (f'%{search_query}%', per_page, (page-1)*per_page,))
    transaction = cur.fetchall()

    cur.execute('''select count(*) from Transaction where t_ID ilike %s''', (f'%{search_query}%',))
    total_transaction = cur.fetchone()[0]
    cur.close()
    conn.close()
    return render_template('retrieve_transaction.html', transaction_list=transaction, page=page, per_page=per_page, total_items=total_transaction, search_query=search_query, sort_by=sort_by, sort_order=sort_order)


@app.route("/transaction/staff/<s_ID>/")
@login_required
@staff_required
def retrieve_staff_transaction(s_ID):
    conn = db_connection()
    cur = conn.cursor()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 't_ID')
    sort_order = request.args.get('sort_order', 'asc')


    query = f"select * from Transaction where s_ID = %s and t_ID ilike %s order by {sort_by} {sort_order} limit %s offset %s"
    cur.execute(query, (s_ID, f'%{search_query}%', per_page, (page-1)*per_page,))
    transaction = cur.fetchall()

    cur.execute('''select count(*) from Transaction where s_ID = %s and t_ID ilike %s''', (s_ID, f'%{search_query}%',))
    total_transaction = cur.fetchone()[0]
    cur.close()
    conn.close()
    return render_template('retrieve_transaction.html', transaction_list=transaction, page=page, per_page=per_page, total_items=total_transaction, search_query=search_query, sort_by=sort_by, sort_order=sort_order)


@app.route("/transaction/customer/<c_ID>/")
@login_required
def retrieve_customer_transaction(c_ID):
    conn = db_connection()
    cur = conn.cursor()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 't_ID')
    sort_order = request.args.get('sort_order', 'asc')


    query = f"select * from Transaction where c_ID = %s and t_ID ilike %s order by {sort_by} {sort_order} limit %s offset %s"
    cur.execute(query, (c_ID, f'%{search_query}%', per_page, (page-1)*per_page,))
    transaction = cur.fetchall()

    cur.execute('''select count(*) from Transaction where c_ID = %s and t_ID ilike %s''', (c_ID, f'%{search_query}%',))
    total_transaction = cur.fetchone()[0]
    cur.close()
    conn.close()
    return render_template('retrieve_transaction.html', transaction_list=transaction, page=page, per_page=per_page, total_items=total_transaction, search_query=search_query, sort_by=sort_by, sort_order=sort_order)


@app.route("/transaction/update/<t_ID>/", methods = ['GET','POST'])
@login_required
@admin_required
def update_transaction(t_ID):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute('''select * from Transaction where t_ID = %s''', (t_ID,))
    transaction = cur.fetchone()
    cur.close()
    conn.close()

    if request.method == 'POST':
        t_ID2 = request.form['t_ID']
        c_ID = request.form['c_ID']
        s_ID = request.form['s_ID']
        t_date = request.form['t_date']
        t_amount = request.form['t_amount']
        t_desc = request.form['t_category']
        conn = db_connection()
        cur = conn.cursor()
        cur.execute('''update Transaction set t_ID = %s, c_ID = %s, s_ID = %s, t_date = %s, t_amount = %s, t_category = %s where t_ID = %s''',
                    (t_ID2, c_ID, s_ID, t_date, t_amount, t_desc, t_ID,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('retrieve_transaction'))
    return render_template('update_transaction.html', transaction = transaction)


@app.route("/transaction/delete/<t_ID>/", methods = ['POST'])
@login_required
@admin_required
def delete_transaction(t_ID):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute('''delete from Transaction where t_ID = %s returning *''', (t_ID,))
    del_item = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    flash(f'Transaction deleted successfully! {del_item}', 'success')
    return redirect(url_for('retrieve_transaction'))


if __name__ == '__main__':
    app.run(debug=True)

