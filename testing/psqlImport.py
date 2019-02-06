from backend.utilities import psqlUtilities as psql
from backend.import import sqlSchema

#Composite Process--------------------------------------------------------------
def importProcedure(connection, csvPath):
    psql.backupTableCSV(connection, 'Users', csvPath+'Users.csv')
    deleteAllTables(connection)
    tables = sqlSchema.compileTables()
    createAllTables(connection, tables)
    bulkFillDatabase(connection, tables,csvPath)

#Base Import Functions----------------------------------------------------------
#Creates all tables mentioned in schema
def createAllTables(connection, tables):
    for table in tables:
        psql.createTable(connection, tables)

#Delete every table in database
def deleteAllTables(connection):
    tables = findAllTableNames(connection)
    for table in tables:
        psql.deleteTable(connection, table)

#Bulk fill 'graph' tables with graph contents
def bulkFillDatabase(connection, tables, path):
    tableNames = [table['name'] for table in tables]
    csvFiles   = ["{0}{1}.csv".format(path, table) for table in tableNames]
    for table in tableNames:
        psql.bulkFillTableCSV(connection, table, csvFile)

#Get a list of all tables inside database
def findAllTableNames(connection):
    return psql.retrieveRecordContents('table_name','information_schema.tables', 'table_schema', 'public')
