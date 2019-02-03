from configparser import ConfigParser
import psycopg2
from couchbase.cluster import Cluster, PasswordAuthenticator
from elasticsearch import Elasticsearch
LOCAL = '/home/xvalier/Documents/curatedTSG/connections2.ini'
CLOUD = '/home/nikilsunilkumar/sets/curatedTSG/connections.ini'

def accessDatabases(cloudString, localString):
    connections = {}
    connectionString = chooseConnectionString(cloudString, localString)
    couch = accessCouch(connectionString)
    connections['couchActive']   = accessCouchBucket(couch, 'active')
    connections['couchArchives'] = accessCouchBucket(couch, 'archives')
    connections['sql']       = accessPSQL(connectionString)
    connections['elastic']   = accessElastic()
    return connections

#Database Access Functions------------------------------------------------------
#Connect to Postgresql Database and return connection object
def accessPSQL(connectionString):
    host, db, user, pw = extractPSQLInfo(connectionString)
    return psycopg2.connect(host=host,database=db,user=user,password=pw)

#Connect to Couchbase Database and return database object
def accessCouch(connectionString):
    user, pw = extractCouchInfo(connectionString)
    database = Cluster()
    auth     = PasswordAuthenticator(user, pw)
    database.authenticate(auth)
    return database

#Connect to specific Couchbase bucket from Couchbase database object
def accessCouchBucket(database, bucket):
    return database.open_bucket(bucket)

#Connect to ElasticSearch Search Engine
def accessElastic():
    return Elasticsearch()

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

#Open connectionString INI file and read its contents
def readINI(file):
    ini = ConfigParser();
    ini.read(file)
    return ini
