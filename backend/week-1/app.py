from flask import Flask
import psycopg2

app = Flask(__name__)
conn = psycopg2.connect("dbname=DSOC user=postgres password=Ab290805")

cur = conn.cursor()

cur.execute(''' create table if not exists InventoryItem(
            Item_SKU varchar(100) primary key,
            Item_Name varchar(100),
            Item_Description varchar(200),
            Item_Price float,
            Item_Qty int)''')

cur.execute(''' create table if not exists Customer(
            c_ID varchar(100) primary key,
            c_name varchar(100),
            c_email varchar(100),
            c_contact varchar(20))''')

cur.execute(''' create table if not exists Staff(
            s_ID varchar(100) primary key,
            s_name varchar(100),
            s_email varchar(100),
            s_isAdmin boolean,
            s_contact varchar(20))''')

cur.execute(''' create table if not exists Transaction(
            t_ID varchar(100) primary key,
            c_ID varchar(100) references Customer(c_ID),
            s_ID varchar(100) references Staff(s_ID), 
            t_date date,
            t_amount float,
            t_category varchar(200))''')
conn.commit()



@app.route("/")
def intro():
    return "hi"
    
if __name__ == '__main__':
    app.run()