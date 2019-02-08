from backend.utilities import toolsSQL as sql
from backend.schema import schemaSQL

#Composite Process--------------------------------------------------------------
def importProcedure(connection, csvPath):
    sql.backupTableCSV(connection, 'Users', csvPath+'Users.csv')
    deleteAllTables(connection)
    tables = schemaSQL.compileTables()
    createAllTables(connection, tables)
    bulkFillDatabase(connection, tables,csvPath)

#Base Import Functions----------------------------------------------------------
#Creates all tables mentioned in schema
def createAllTables(connection, tables):
    for table in tables:
        sql.createTable(connection, tables)

#Delete every table in database
def deleteAllTables(connection):
    tables = findAllTableNames(connection)
    for table in tables:
        sql.deleteTable(connection, table)

#Bulk fill 'graph' tables with graph contents
def bulkFillDatabase(connection, tables, path):
    tableNames = [table['name'] for table in tables]
    csvFiles   = ["{0}{1}.csv".format(path, table) for table in tableNames]
    for table in tableNames:
        sql.bulkFillTableCSV(connection, table, csvFile)

#Get a list of all tables inside database
def findAllTableNames(connection):
    return sql.retrieveRecordContents('table_name','information_schema.tables', 'table_schema', 'public')
