from flask import Flask
import psycopg2

app = Flask(__name__)
conn = psycopg2.connect("dbname=DSOC user=postgres password=Ab290805")

cur = conn.cursor()

cur.execute(''' create table if not exists InventoryItem(
            Item_SKU varchar(100) primary key,
            Item_Name varchar(100),
            Item_Description varchar(200),
            Item_Price float check (Item_Price > 0),
            Item_Qty int check (Item_Qty > -1))''')

cur.execute(''' create table if not exists Customer(
            c_ID varchar(100) primary key,
            c_name varchar(100),
            c_email varchar(100) check (c_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
            c_contact varchar(20))''')

cur.execute(''' create table if not exists Staff(
            s_ID varchar(100) primary key,
            s_name varchar(100),
            s_email varchar(100) check (s_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
            s_isAdmin boolean,
            s_contact varchar(20))''')

cur.execute(''' create table if not exists Transaction(
            t_ID varchar(100) primary key,
            c_ID varchar(100) references Customer(c_ID),
            s_ID varchar(100) references Staff(s_ID), 
            t_date date,
            t_amount float check (t_amount > 0),
            t_category varchar(200))''')

# cur.execute(''' create index inventory_sku_index on InventoryItem(Item_SKU)''')
# cur.execute(''' create index customer_id_index on Customer(c_ID)''')
# cur.execute(''' create index staff_if_index on Staff(s_ID)''')
# cur.execute(''' create index transaction_id_index on Transaction(t_ID)''')
# cur.execute(''' create index transaction_date_index on Transaction(t_date)''')

# cur.execute('''insert into InventoryItem values ('I1', 'Lays', 'Chips', 20, 40),
#             ('I2', 'Oreo', 'Biscuit', 30, 100)''')

# cur.execute('''insert into Customer values ('C1', 'Aditya', 'abg@gmail.com', '939239230'),
#             ('C2', 'Parv', 'asb@gmail.com', '2i91310931')''')
# cur.execute('''insert into Staff values ('S1', 'Raghav', 'ajd@gmail.com', True, '20392481291'),
#             ('S2', 'Rohan', 'ajsak@gmail.com', False, '29392382031')''')
# cur.execute('''insert into Transaction values ('T1', 'C1', 'S1', '2024-6-24', 122, 'food'),
#             ('T2', 'C2', 'S1', '2024-6-25', 200, 'food' )''')
conn.commit()

cur.close()
conn.close()


@app.route("/")
def intro():
    return "hi"


@app.route("/inventory/<itemsku>")
def get_inventory(itemsku):
    conn = psycopg2.connect("dbname=DSOC user=postgres password=Ab290805")
    cur = conn.cursor()
    cur.execute('''select Item_Price, Item_Qty from InventoryItem where Item_SKU = %s''',(itemsku,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {'Qty in Inventory' : data[0][1], 'Value of Inventory' : data[0][0]*data[0][1]}

@app.route("/transaction/customer/<cid>")
def get_cust_trans(cid):
    conn = psycopg2.connect("dbname=DSOC user=postgres password=Ab290805")
    cur = conn.cursor()
    cur.execute('''select * from Transaction where c_ID = %s''',(cid,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {f"Transactions of customer {cid}" : data}

@app.route("/transaction/staff/<sid>")
def get_staff_trans(sid):
    conn = psycopg2.connect("dbname=DSOC user=postgres password=Ab290805")
    cur = conn.cursor()
    cur.execute('''select * from Transaction where s_ID = %s''',(sid,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {f"Transactions of staff {sid}" : data}

@app.route("/transaction/date/<date>")
def get_trans_date(date):
    conn = psycopg2.connect("dbname=DSOC user=postgres password=Ab290805")
    cur = conn.cursor()
    cur.execute('''select * from Transaction where t_date = %s''',(date,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {f"Transactions on date {date}" : data}


if __name__ == '__main__':
    app.run()