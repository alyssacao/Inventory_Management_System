-- Retrieve all orders
-- Description: Fetch all records from Orders table.
SELECT * FROM Orders;

-- Count the number of orders
-- Description: Counts the total number of orders in the database.
SELECT COUNT(*) AS TotalOrders FROM Orders;

-- Find top 5 customers by Total Spending
-- Description: Retrieves the top 5 customers who have spent the most.
SELECT c.Customer_id, c.FirstName, c.LastName, SUM(o.TotalAmount) AS TotalSpent
FROM Customers c JOIN Orders o ON c.customer_id = o.customer_id
GROUP BY c.Customer_id, c.FirstName, c.LastName
ORDER BY TotalSpent DESC
LIMIT 5;

-- Monthly Sales Summary (OLAP - Grouping Sets)
-- Description: Calculates total sales per month and an overall total.
SELECT EXTRACT(YEAR FROM OrderDate) AS Year,
       EXTRACT(MONTH FROM OrderDate) AS Month,
       SUM(TotalAmount) AS TotalSales
FROM Orders
GROUP BY GROUPING SETS ((EXTRACT(YEAR FROM OrderDate), EXTRACT(MONTH FROM OrderDate)), ())
ORDER BY Year, Month;

-- Average Order Value per Customer
-- Description: Calculate the average order value per customer
SELECT Customer_id, ROUND(AVG(TotalAmount),2) AS AvgOrderValue
FROM Orders
GROUP BY Customer_id
ORDER BY AvgOrderValue DESC;

-- Rank Customer by Total Spending (Window Function)
-- Description: Assigns a ranking to customers based on their total spending.
SELECT c.Customer_id, c.FirstName, c.LastName, 
	SUM(o.TotalAmount) AS TotalSpent,
	DENSE_RANK() OVER (ORDER BY SUM(o.TotalAmount) DESC) AS Rank
FROM Customers c JOIN Orders o ON c.Customer_id = o.customer_id
GROUP BY c.Customer_id, c.FirstName, c.LastName;

-- Find Customers with No Orders
-- Description: Lists customers who have not placed any orders
SELECT c.Customer_id, c.FirstName, c.LastName
FROM Customers c
LEFT JOIN Orders o ON c.Customer_id = o.Customer_id
WHERE o.Order_id IS NULL;

-- List Orders with more than 3 Items
-- Description: Retrieves orders that have more than 3 different products
SELECT Order_id, COUNT(*) AS ItemCount
FROM OrderDetails
GROUP BY Order_id
HAVING COUNT(*) > 3;

-- Split Orders into Quartiles by Amount (NTILE)
-- Description: Categorizes orders into 4 quartiles based on order value, aiming for distributing customers into groups for specific business strategies.
SELECT 
    Order_id,
    TotalAmount,
    NTILE(4) OVER (ORDER BY TotalAmount) AS AmountQuartile
FROM Orders;

-- Calculate Running Total of Sales (Window Function)
-- Description: Computes cumulative total sales over time.
SELECT OrderDate, SUM(TotalAmount) OVER (ORDER BY OrderDate) AS RunningTotal
FROM Orders;

-- Most Popular Products by Quantity Sold
-- Description: Find the top-selling products.
SELECT p.Product_id, p.PName, SUM(od.Quantity) AS TotalQuantitySold
FROM OrderDetails od
JOIN Products p ON od.Product_id = p.Product_id
GROUP BY p.Product_id, p.PName
ORDER BY TotalQuantitySold DESC
LIMIT 5;

-- Find the First and Last Order Dates per Customer
-- Description: Displays the first and most recent order for each customer.
SELECT Customer_id, 
       MIN(OrderDate) AS FirstOrder,
       MAX(OrderDate) AS LastOrder
FROM Orders
GROUP BY Customer_id;

-- Finds Orders Placed on Weekends
-- Description: Extracts orders placed on Saturdays and Sundays.
SELECT * FROM Orders WHERE EXTRACT(DOW FROM OrderDate) IN (0, 6);

-- Percentage Contribution of Each Customer’s Spending
-- Description: Calculate each customer’s contribution to total sales.
SELECT Customer_id, 
       SUM(TotalAmount) AS TotalSpent,
       ROUND(SUM(TotalAmount) * 100.0 / SUM(SUM(TotalAmount)) OVER (), 2) AS PercentOfTotal
FROM Orders
GROUP BY Customer_id;

-- Detect Products Never Order
-- Description: Lists products that have never been ordered by any customer.
SELECT Product_id, PName
FROM Products
WHERE Product_id NOT IN (
    SELECT DISTINCT Product_id FROM OrderDetails
);

-- Total Sales per Product Category
-- Description: Aggregates total sales across different product categories.
SELECT p.Category_id, SUM(od.Quantity * od.UnitPrice) AS TotalCategorySales
FROM OrderDetails od
JOIN Products p ON od.Product_id = p.Product_id
GROUP BY p.Category_id
ORDER BY TotalCategorySales DESC;

-- Customer Order Frequency (Window Function)
-- Counts how many times a customer has placed an order.
SELECT Customer_id, COUNT(Order_id) AS OrderCount,
       DENSE_RANK() OVER (ORDER BY COUNT(Order_id) DESC) AS FrequencyRank
FROM Orders
GROUP BY Customer_id;

-- Monthly Revenue Growth Rate (LAG Function)
-- Description: Computes the month-over-month sales growth rate.
SELECT EXTRACT(YEAR FROM OrderDate) AS Year,
       EXTRACT(MONTH FROM OrderDate) AS Month,
       SUM(TotalAmount) AS MonthlySales,
       LAG(SUM(TotalAmount)) OVER (ORDER BY EXTRACT(YEAR FROM OrderDate), EXTRACT(MONTH FROM OrderDate)) AS PrevMonthSales,
       ROUND((SUM(TotalAmount) - LAG(SUM(TotalAmount)) OVER ()) / LAG(SUM(TotalAmount)) OVER () * 100,2) AS GrowthRate
FROM Orders
GROUP BY Year, Month
ORDER BY Year, Month;

