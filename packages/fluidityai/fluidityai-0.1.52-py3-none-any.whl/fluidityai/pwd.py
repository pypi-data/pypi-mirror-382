import duckdb as db

first_name, last_name = task_outputs["User Name"].split()
dob = task_outputs["DOB"]
email = task_outputs["Email"]
customersDF = task_outputs["Loader"]["Customers"]

resultsDF = db.sql(
    f"SELECT password FROM customersDF WHERE LOWER(first_name)='{first_name.lower()}' \
    AND LOWER(last_name)='{last_name.lower()}' AND date_of_birth='{dob}' AND LOWER(email)='{email.lower()}'").df()

if resultsDF.shape[0] == 1:
    password = resultsDF.at[0, 'password']