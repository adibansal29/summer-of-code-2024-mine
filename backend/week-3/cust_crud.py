from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import psycopg2
from flask_login import LoginManager

app = Flask(__name__)

conn = psycopg2.connect("dbname=DSOC user=postgres password=Ab290805")
cur = conn.cursor()

login_manager = LoginManager()
# cur.execute(''' alter table Staff add column is_approved boolean''')
# cur.execute(''' alter table Staff add column s_password varchar(100)''')
# cur.execute(''' alter table Customer add column c_password varchar(100)''')



#staff CRUD Operations
app.secret_key = '12d'
def db_connection():
    conn = psycopg2.connect("dbname=DSOC user=postgres password=Ab290805")
    return conn

@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/staff/create/", methods=['GET','POST'])
def create_staff():
    if request.method == 'POST':
        s_ID = request.form['s_ID']
        s_name = request.form['s_name']
        s_email = request.form['s_email']
        s_contact = request.form['s_contact']
        s_isAdmin = request.form['s_isAdmin']
        is_approved = request.form['is_approved']
        s_password = request.form['s_password']
        conn = db_connection()
        cur = conn.cursor()
        cur.execute(''' insert into Staff values (%s, %s, %s, %s, %s, %s, %s)'''
                    ,(s_ID, s_name, s_email, s_isAdmin, s_contact, is_approved, s_password,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Staff created successfully!', 'success')
        return redirect(url_for('retrieve_staff'))
    return render_template('create_staff.html')


@app.route("/staff/retrieve/", defaults={'s_ID': None})
@app.route("/staff/<s_ID>/")
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
        conn = db_connection()
        cur = conn.cursor()
        cur.execute('''update Staff set s_ID = %s, s_name = %s, s_email = %s, s_contact = %s, s_isAdmin = %s, is_approved = %s, s_password = %s where s_ID = %s''',
                    (s_ID2, s_name, s_email, s_contact, s_isAdmin, is_approved, s_password, s_ID,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Staff updated successfully!', 'success')
        return redirect(url_for('retrieve_staff'))
    return render_template('update_staff.html', staff = staff)


@app.route("/staff/delete/<s_ID>/", methods = ['POST'])
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
        c_password = request.form['c_password']
        conn = db_connection()
        cur = conn.cursor()
        cur.execute(''' insert into Customer values (%s, %s, %s, %s, %s)'''
                    ,(c_ID, c_name, c_email, c_contact, c_password,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Customer created successfully!', 'success')
        return redirect(url_for('retrieve_customer'))
    return render_template('create_customer.html')


@app.route("/customer/retrieve/", defaults={'c_ID': None})
@app.route("/customer/<c_ID>/")
def retrieve_customer(c_ID):
    conn = db_connection()
    cur = conn.cursor()

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
        conn = db_connection()
        cur = conn.cursor()
        cur.execute('''update Customer set c_ID = %s, c_name = %s, c_email = %s, c_contact = %s, c_password = %s where c_ID = %s''',
                    (c_ID2, c_name, c_email, c_contact, c_password, c_ID,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('retrieve_customer'))
    return render_template('update_customer.html', customer = customer)


@app.route("/customer/delete/<c_ID>/", methods = ['POST'])
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


if __name__ == '__main__':
    app.run(debug=True)