queries = {
        "top_inventory_and_sales": """
            SELECT p.product_id, p.pname
            FROM products p 
            JOIN (SELECT product_id 
	              FROM products 
	              WHERE stockquantity > 20
	              INTERSECT
	              SELECT product_id 
	              FROM orderdetails 
	              WHERE quantity > 18) as topsales
            ON p.product_id= topsales.product_id;
        """,
        "products_not_ordered": """
			SELECT product_id, pname
			FROM products
			WHERE product_id NOT IN
   			                    (SELECT DISTINCT product_id FROM OrderDetails);
        """,
        "sales_summary": """
            SELECT EXTRACT (YEAR FROM OrderDate) AS YEAR,
	               EXTRACT (MONTH FROM OrderDate) AS MONTH,
	               SUM(TotalAmount) AS TotalSales
                   FROM Orders
                   GROUP BY GROUPING SETS ((EXTRACT(YEAR FROM OrderDate),
						EXTRACT(MONTH FROM OrderDate)),
						())
                    ORDER BY Year, Month;
        """,
        "customer_rank": """
            SELECT c.FirstName, c.LastName,
                    SUM(o.TotalAMount) AS TotalSpent,
                    DENSE_RANK() OVER (ORDER BY SUM(o.TotalAmount) DESC) AS Rank
            FROM Customers c JOIN Orders o ON c.Customer_id = o.Customer_id
            GROUP BY c.FirstName, c.LastName;
        """,
        "top_selling": """
            WITH monthly_sales AS (
                            SELECT od.product_id,
                                SUM(od.quantity) AS total_sold
                            FROM orderdetails od JOIN Orders o ON od.Order_id = o.Order_id
                            WHERE o.orderdate >= '2025-03-01' 
      								AND o.orderdate < '2025-04-01'
                            GROUP BY od.product_id
                            )

            SELECT p.pname AS product_name,
                    ms.total_sold
            FROM monthly_sales ms
            JOIN products p ON ms.product_id = p.product_id
            ORDER BY ms.total_sold DESC
            LIMIT 5;
        """,
        "expensive_products_than_garden" : """
            SELECT p.product_id, 
                    p.pname, 
                    p.priceperunit
            FROM products p
            WHERE p.priceperunit > ALL (
                    SELECT priceperunit 
                    FROM products 
                    JOIN category c ON products.category_id = c.category_id
                    WHERE c.categoryname = 'Garden'

                    );
                    """
    }