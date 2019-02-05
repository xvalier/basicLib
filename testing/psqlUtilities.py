import psycopg2

#Composite Functions------------------------------------------------------------
#Generic Function to check if a user exists in SQL based on specified property
def checkRecordExists(connection, table, property, value):
    entryExists = 0
    query = genericQuery('1',table,property,value)
    results = executeQuery(connection, query)
    if len(results) > 0:
        entryExists = 1
    return entryExists

#Executes generic Read Query and returns unwrapped results
def retriveRecordContents(connection, product, table, condition, value):
    query   = genericQuery(product,table,condition, value)
    results = executeQuery(connection, query)
    return unwrapResults(results)

#CSV to SQL Export/Import Functions---------------------------------------------
#Bulk fill in a table with CSV contents
def bulkFillTableCSV(connection, table, csvFile):
    command = "COPY {0} FROM {1} WITH CSV HEADER DELIMITER ','".format(table, csvFile)
    executeCommand(connection, command)

#Export psql table to CSV (mostly to retain user info when performing graph import)
def backupTableCSV(connection, table, csvFile):
    command = "COPY {0} TO {1} WITH CSV HEADER DELIMITER ','".format(table, csvFile)
    executeCommand(connection, command)

#SQL CRUD Functions-------------------------------------------------------------
#Generic Function to create a table (using tableNames,tableContents as schema)
def createTable(connection, table):
    command = "CREATE TABLE IF NOT EXISTS {0}({1})"
    command = command.format(table['name'], table['content'])
    executeCommand(connection, command)

#Generic Function to delete a table
def deleteTable(connection, table):
    command = "DROP TABLE IF EXISTS {0}".format(table)
    executeCommand(connection, command)

#Generic Function to create a single record in specified table
def createRecord(connection, table, *arguments):
    values  = aggregateParameters(arguments)
    command = "INSERT INTO {0} VALUES ({1})".format(table, values)
    executeCommand(connection, command)

#Generic Function to update a single record
def updateRecord(connection, table, modProperty, modValue, condition):
    command = "UPDATE '{0}' SET {1} = '{2}' WHERE {3}"
    command = command.format(table, modProperty, modValue, condition)
    executeCommand(command)

#Generic Function to delete a record from specified table
def deleteRecord(connection, table, property, value):
    command = "DELETE FROM {0} WHERE {1} = {2}".format(table, property, value)
    executeCommand(connection, command)

#Compiles a SQL VALUES string for varying lengths of arguments
def aggregateParameters(arguments):
    values = ''
    param  = "'{0}'"
    for arg in arguments:
        values = "{0}{1}{2}".format(values,param.format(arg),',')
    return values[0:len(values)-1]

#BASE SQL Functions-------------------------------------------------------------
#Connect to PostgreSQL Database via Credentials
def accessPSQL(host, db, user, pw):
    return psycopg2.connect(host=host,database=db,user=user,password=pw)

#Fills in generic SQL query with specific variable data
def genericQuery(product, table, condition, value):
    query = "SELECT {0} FROM {1} WHERE {2} = '{3}'"
    query = query.format(product, table, condition, value)
    return query

#Extracts query results into list format
def unwrapResults(results):
    return [results[0] for result in results]

#Execute SQL Query in Postgresql and return results (for read transactions)
def executeQuery(connection, query):
    database = connection.cursor()
    database.execute(query)
    results  = database.fetchall()
    database.close()
    connection.commit()
    return results

#Execute a SQL command in Postgresql (for create, update, delete transactions)
def executeCommand(connection, command):
    database = connection.cursor()
    database.execute(command)
    database.close()
    connection.commit()
