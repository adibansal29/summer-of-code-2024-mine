from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import psycopg2
from flask_login import LoginManager

app = Flask(__name__)
conn = psycopg2.connect("dbname=DSOC user=postgres password=Ab290805")
cur = conn.cursor()

login_manager = LoginManager()

# cur.execute(''' alter table Staff add column is_approved boolean''')
#cur.execute(''' alter table Staff add column s_password varchar(100)''')





#Staff CRUD Operations
app.secret_key = '12d'
def db_connection():
    conn = psycopg2.connect("dbname=DSOC user=postgres password=Ab290805")
    return conn

@app.route("/")
def hello():
    return redirect(url_for('retrieve_staff'))


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


@app.route("/store/delete/<s_ID>/", methods = ['POST'])
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


if __name__ == '__main__':
    app.run(debug=True)