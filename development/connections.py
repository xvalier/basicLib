from configparser import ConfigParser
from backend.utilities import toolsCouch as couch
from backend.utilities import toolsElastic as elastic
from backend.utilities import toolsSQL as sql

#Connect to Couchbase and ElasticSearch for Search microservice
def connectSearch(connectionString):
    user, pw               = extractCouchInfo(connectionString)
    connections            = couch.accessCouch(user, pw)
    connections['elastic'] = accessElastic()
    return connections

#Connect to Postgresql and ElasticSearch for Import microservice
def connectImport(connectionString):
    host, db, user, pw     = extractPSQLInfo(connectionString)
    connections['psql']    = accessPSQL(host, db, user, pw)
    connections['elastic'] = accessElastic()
    connections['csv']     = extractCSVPath(connection)
    return connections

#Connect to Postgresql for Auth microservice
def connectAuth(connectionString):
    host, db, user, pw     = extractPSQLInfo(connectionString)
    connections['psql']    = accessPSQL(host, db, user, pw)
    return connections

#ConnectionString Functions-----------------------------------------------------
#Determine location of connectionString based on type of server
def chooseConnectionString(cloudString, localString):
    answer = 0
    while((answer != 1) & (answer != 2)):
        print('Is this on (1) GCP or (2) Personal laptop?')
        answer = input('Choose either 1 or 2:')
        if answer == '1':
            return cloudString
        elif answer == '2':
            return localString
        else:
            print('Please choose either 1 or 2')

#Extraction Functions-----------------------------------------------------------
#Extract gRPC client stub info based on connectionString
def extractClientGRPCInfo(file):
    connectionString = readINI(file)
    address  = connectionString['grpc']['clientAddr']
    port     = int(connectionString['grpc']['port'])
    return address,port

#Extract gRPC server info based on connectionString
def extractServerGRPCInfo(file):
    connectionString = readINI(file)
    address  = connectionString['grpc']['serverAddr']
    port     = int(connectionString['grpc']['port'])
    return address,port

#Extract Postgresql SQL database info based on connectionString
def extractPSQLInfo(file):
    connectionString = readINI(file)
    host  = connectionString['postgresql']['host']
    db    = connectionString['postgresql']['database']
    user  = connectionString['postgresql']['user']
    pw    = connectionString['postgresql']['password']
    return host, db, user, pw

#Extract Couchbase Document Store database info based on connectionString
def extractCouchInfo(file):
    connectionString = readINI(file)
    user  = connectionString['couchbase']['user']
    pw    = connectionString['couchbase']['password']
    return user, pw

#Extract ElasticSearch search engine info based on connectionString
def extractElasticInfo(file):
    connectionString = readINI(file)
    host  = connectionString['elasticsearch']['host']
    db    = connectionString['elasticsearch']['port']
    return host, db

#Extract information on directories where CSV files are stored
def extractCSVPath(file):
    connectionString = readINI(file)
    return connectionString['csv']['path']

#Open connectionString INI file and read its contents
def readINI(file):
    ini = ConfigParser();
    ini.read(file)
    return ini
