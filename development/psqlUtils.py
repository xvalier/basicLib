#General PSQL LowLevel Functions (mostly for CRUD Operations)
#-------------------------------------------------------------------------------

#Generic Function to check if a user exists in SQL based on specified property
def checkRecordExists(connection, table, property, value):
    entryExists = 0
    query = createQuery('1',table,property,value)
    results = executeQuery(connection, query)
    if len(results) > 0:
        entryExists = 1
    return entryExists

#Executes generic Read Query and returns unwrapped results
def getRecord(connection, product, table, condition, value):
    query   = createQuery(product,table,condition, value)
    results = executeQuery(connection, query)
    return unwrapResults(results)

#Fills in generic SQL query with specific variable data
def createQuery(product, table, condition, value):
    query = "SELECT {0} FROM {1} WHERE {2} = '{3}'"
    query = query.format(product, table, condition, value)
    return query

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
    database = openSQLTransaction(connection)
    database = connection.cursor()
    database.execute(command)
    database.close()
    connection.commit()

#Extracts query results into list format
def unwrapResults(results):
    return [results[0] for result in results]
