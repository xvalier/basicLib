import psycopg2
from utilities import csvUtils as spread
from schemas import psqlSchema as schema
filespath             = '/home/xvalier/Documents/curatedTSG/files/'             #MOVE to import
schema            = '/home/xvalier/Documents/curatedTSG/schemas/schema.csv'     #MOVE to import

#Functions to create
#General getRecord
#General clearTable --> Delete and Recreate?
#General fillTable with CSV contents --> rename migrateCSV?
#General parseSchema that takes in a 'schema' file and creates contents based on it
#Overall 'clean' table contents function
#Overall create schema function

#MOVE TO IMPORT
#Connect to psql database, create schema and fill with csv contents
def initialization(connectionString,path):
    connection = ini.readConnectionStringSQL(connectionString)
    deleteTables(connection)
    createTables(connection)
    fillTables(connection,path)

#CREATE Functions---------------------------------------------------------------
#Automatic script to create Users Table in PSQL
def createAllTables(connection, tables):
    for table in tables:
        createTable(connection, tables)

#Generic Function to create a table (using tableNames,tableContents as schema)
def createTable(connection, table):
    command = "CREATE TABLE IF NOT EXISTS {0}({1})"
    command = command.format(table['name'], table['content'])
    executeCommand(connection, command)

#Generic Function to create a single record in specified table
def createRecord(connection, table, *arguments):
    values  = aggregateParameters(arguments)
    command = "INSERT INTO {0} VALUES ({1})".format(table, values)
    executeCommand(connection, command)

#Compiles a SQL VALUES string for varying lengths of arguments
def aggregateParameters(arguments):
    values = ''
    param  = "'{0}'"
    for arg in arguments:
        values = "{0}{1}{2}".format(values,param.format(arg),',')
    return values[0:len(values)-1]

#EXPORT/IMPORT CSV FUNCTIONS----------------------------------------------------
#Bulk fill 'graph' tables with graph contents
def bulkFillDatabase(connection, tables, path):
    tableNames = [table['name'] for table in tables]
    csvFiles   = ["{0}{1}.csv".format(path, table) for table in tableNames]
    for table in tableNames:
        bulkFillTableCSV(connection, table, csvFile)

#Bulk fill in a table with CSV contents
def bulkFillTableCSV(connection, table, csvFile):
    command = "COPY {0} FROM {1} WITH CSV HEADER DELIMITER ','".format(table, csvFile)
    executeCommand(connection, command)

#Export psql table to CSV (mostly to retain user info when performing graph import)
def backupTableCSV(connection, table, csvFile):
    command = "COPY {0} TO {1} WITH CSV HEADER DELIMITER ','".format(table, csvFile)
    executeCommand(connection, command)

#READ Functions-----------------------------------------------------------------
#Get a list of all tables inside database
def findAllTableNames(connection):
    return getRecord('table_name','information_schema.tables', 'table_schema', 'public')

#UPDATE Functions---------------------------------------------------------------
def updateRecord(connection, table, modProperty, modValue, condition):
    command = "UPDATE '{0}' SET {1} = '{2}' WHERE {3}"
    command = command.format(table, modProperty, modValue, condition)
    executeCommand(command)

#DELETE Functions---------------------------------------------------------------
#Delete every table (to retain Users, backup the table then delete)
def deleteAllTables(connection):
    tables = findAllTableNames(connection)
    for table in tables:
        deleteTable(connection, table)

#Generic Function to delete a table
def deleteTable(connection, table):
    command = "DROP TABLE IF EXISTS {0}".format(table)
    executeCommand(connection, command)

#Generic Function to delete a record from specified table
def deleteRecord(connection, table, property, value):
    command = "DELETE FROM {0} WHERE {1} = {2}".format(table, property, value)
    executeCommand(connection, command)

#ConnectionString Functions-----------------------------------------------------
connectionString = '/home/xvalier/Documents/curatedTSG/connections2.ini'
def accessPSQL(connectionString):
    host, db, user, pw = extractPSQLInfo(connectionString)
    return psycopg2.connect(host=host,database=db,user=user,password=pw)

def extractPSQLInfo(file):
    connectionString = readINI(file)
    host  = connectionString['postgresql']['host']
    db    = connectionString['postgresql']['database']
    user  = connectionString['postgresql']['user']
    pw    = connectionString['postgresql']['password']
    return host, db, user, pw

#Open connectionString INI file and read its contents
def readINI(file):
    ini = ConfigParser();
    ini.read(file)
    return ini
