import duckdb as db

email = task_outputs["Email"]
customersDF = task_outputs["Loader"]["Customers"]
ordersDF = task_outputs["Loader"]["Orders"]
orderDetailsDF = task_outputs["Loader"]["OrderDetails"]

userOrderDetailsDF = db.sql(f"SELECT o.order_date, o.status, o.expected_delivery_date, od.item, od.price \
    FROM customersDF c INNER JOIN ordersDF o ON c.account_id = o.account_id \
    INNER JOIN orderDetailsDF od on o.order_id = od.order_id WHERE LOWER(c.email)='{email.lower()}'").df()

result = userOrderDetailsDF
