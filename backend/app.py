from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import psycopg2.extras
from flask_cors import CORS
from queries.report_queries import queries

app = Flask(__name__)
CORS(app)


# PostgreSQL connection
conn = psycopg2.connect(
    dbname="InventoryManagementSystem",
		user="postgres",
		password="thuydieuu3011",
		host="localhost",
		port="5432"
)
cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
# # Function to fetch inventory data
# def get_inventory():
#     conn = sqlite3.connect('InventoryManagementSystem')
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM products")
#     data = cursor.fetchall()
#     conn.close()
#     return data

@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@app.route('/get_tables')
def get_tables():
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = [row['table_name'] for row in cursor.fetchall()]
    return jsonify(tables)

@app.route('/table_metadata/<table>')
def get_columns(table):
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = %s
    """, (table,))
    return jsonify(cursor.fetchall())

@app.route('/create/<table>', methods=['POST'])
def create_row(table):
    data = request.json
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['%s'] * len(data))
    values = list(data.values())
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, values)
    conn.commit()
    return 'Row added successfully'

@app.route('/read/<table>')
def read_table(table):
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    return jsonify(rows)

@app.route('/update/<table>', methods=['POST'])
def update_row(table):
    data = request.json
    query = f"UPDATE {table} SET {data['upd_col']} = %s WHERE {data['id_col']} = %s"
    cursor.execute(query, (data['upd_val'], data['id_val']))
    conn.commit()
    return 'Row updated successfully'

@app.route('/delete/<table>', methods=['POST'])
def delete_row(table):
    data = request.json
    query = f"DELETE FROM {table} WHERE {data['col']} = %s"
    cursor.execute(query, (data['val'],))
    conn.commit()
    return 'Row deleted successfully'

@app.route('/report/<report_name>')
def report(report_name):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Always start with rollback to clean up any previous failed transaction
    conn.rollback()

    # queries = {
    #     "top_inventory_and_sales": """
    #         SELECT p.product_id, p.pname
    #         FROM products p 
    #         JOIN (SELECT product_id 
	#               FROM products 
	#               WHERE stockquantity > 20
	#               INTERSECT
	#               SELECT product_id 
	#               FROM orderdetails 
	#               WHERE quantity > 18) as topsales
    #         ON p.product_id= topsales.product_id;
    #     """,
    #     "products_not_ordered": """
	# 		SELECT product_id, pname
	# 		FROM products
	# 		WHERE product_id NOT IN
   	# 		                    (SELECT DISTINCT product_id FROM OrderDetails);
    #     """,
    #     "sales_summary": """
    #         SELECT EXTRACT (YEAR FROM OrderDate) AS YEAR,
	#                EXTRACT (MONTH FROM OrderDate) AS MONTH,
	#                SUM(TotalAmount) AS TotalSales
    #                FROM Orders
    #                GROUP BY GROUPING SETS ((EXTRACT(YEAR FROM OrderDate),
	# 					EXTRACT(MONTH FROM OrderDate)),
	# 					())
    #                 ORDER BY Year, Month;
    #     """,
    #     "customer_rank": """
    #         SELECT c.FirstName, c.LastName,
    #                 SUM(o.TotalAMount) AS TotalSpent,
    #                 DENSE_RANK() OVER (ORDER BY SUM(o.TotalAmount) DESC) AS Rank
    #         FROM Customers c JOIN Orders o ON c.Customer_id = o.Customer_id
    #         GROUP BY c.FirstName, c.LastName;
    #     """,
    #     "top_selling": """
    #         WITH monthly_sales AS (
    #                         SELECT od.product_id,
    #                             SUM(od.quantity) AS total_sold
    #                         FROM orderdetails od JOIN Orders o ON od.Order_id = o.Order_id
    #                         WHERE o.orderdate >= '2025-03-01' 
    #   								AND o.orderdate < '2025-04-01'
    #                         GROUP BY od.product_id
    #                         )

    #         SELECT p.pname AS product_name,
    #                 ms.total_sold
    #         FROM monthly_sales ms
    #         JOIN products p ON ms.product_id = p.product_id
    #         ORDER BY ms.total_sold DESC
    #         LIMIT 5;
    #     """,
    #     "expensive_products_than_garden" : """
    #         SELECT p.product_id, 
    #                 p.pname, 
    #                 p.priceperunit
    #         FROM products p
    #         WHERE p.priceperunit > ALL (
    #                 SELECT priceperunit 
    #                 FROM products 
    #                 JOIN category c ON products.category_id = c.category_id
    #                 WHERE c.categoryname = 'Garden'

    #                 );
    #                 """
    # }

    sql = queries.get(report_name)
    if not sql:
        return jsonify({"error": "Unknown report"}), 400

    try:
        cur.execute(sql)
        rows = [dict(row) for row in cur.fetchall()]
        return jsonify(rows)
    except Exception as e:
        conn.rollback()
        print(f"Report '{report_name}' failed with error: {e}")  # Add this line
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


if __name__ == '__main__':
    app.run(debug=True)
