from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
app.secret_key = '12d'
def db_connection():
    conn = psycopg2.connect("dbname=DSOC user=postgres password=Ab290805")
    return conn

@app.route("/")
def hello():
    return redirect(url_for('retrieve_product'))


@app.route("/inventory/create/", methods=['GET','POST'])
def create_product():
    if request.method == 'POST':
        item_sku = request.form['Item_SKU']
        item_name = request.form['Item_Name']
        item_description = request.form['Item_Description']
        item_price = request.form['Item_Price']
        item_qty = request.form['Item_Qty']
        conn = db_connection()
        cur = conn.cursor()
        cur.execute(''' insert into InventoryItem values (%s, %s, %s, %s, %s)''',(item_sku, item_name, item_description, item_price, item_qty,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Product created successfully!', 'success')
        return redirect(url_for('retrieve_product'))
    return render_template('create_product.html')


@app.route("/inventory/retrieve/", defaults={'item_sku': None})
@app.route("/inventory/<item_sku>/")
def retrieve_product(item_sku):
    conn = db_connection()
    cur = conn.cursor()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'Item_SKU')
    sort_order = request.args.get('sort_order', 'asc')

    if item_sku:
        cur.execute('''select * from InventoryItem where Item_SKU = %s''', (item_sku,))
        items = cur.fetchone()

    else:
        query = f"select * from InventoryItem where Item_Name ilike %s order by {sort_by} {sort_order} limit %s offset %s"
        cur.execute(query, (f'%{search_query}%', per_page, (page-1)*per_page,))
        items = cur.fetchall()    

    cur.execute('''select count(*) FROM InventoryItem where Item_Name ilike %s''', (f'%{search_query}%',))
    total_items = cur.fetchone()[0]
    cur.close()
    conn.close()
    return render_template('retrieve_product.html', products=items, page=page, per_page=per_page, total_items=total_items, search_query=search_query, sort_by=sort_by, sort_order=sort_order)


@app.route("/inventory/update/<item_sku>/", methods = ['GET','POST'])
def update_product(item_sku):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute('''select * from InventoryItem where Item_SKU = %s''', (item_sku,))
    item = cur.fetchone()
    cur.close()
    conn.close()

    if request.method == 'POST':
        item_sku2 = request.form['Item_SKU']
        item_name = request.form['Item_Name']
        item_description = request.form['Item_Description']
        item_price = request.form['Item_Price']
        item_qty = request.form['Item_Qty']
        conn = db_connection()
        cur = conn.cursor()
        cur.execute('''update InventoryItem set Item_SKU = %s, Item_Name = %s, Item_Description = %s, Item_Price = %s, Item_Qty = %s where Item_SKU = %s''',
                    (item_sku2, item_name, item_description, item_price, item_qty, item_sku,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('retrieve_product'))
    return render_template('update_product.html', product = item)


@app.route("/inventory/delete/<item_sku>/", methods = ['POST'])
def delete_product(item_sku):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute('''delete from InventoryItem where Item_SKU = %s returning *''', (item_sku,))
    del_item = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    flash(f'Product deleted successfully! {del_item}', 'success')
    return redirect(url_for('retrieve_product'))


if __name__ == '__main__':
    app.run(debug = True)

