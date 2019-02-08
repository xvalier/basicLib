from backend.helpers import timestamp as time
from couchbase.n1ql import N1QLQuery, CONSISTENCY_REQUEST
import couchbase.subdocument as sd

#Connection Functions-----------------------------------------------------------
#Obtain connections objects for all couchbase buckets
def accessCouch(connectionString):
    connections = {}
    database = accessDatabase(connectionstring)
    connections['couchActive'] = accessBucket(database, 'active')
    connections['couchArchives'] = accessBucket(database, 'archives')
    return connections

#Connect to Couchbase Database and return database object
def accessDatabase(user, pw):
    database = Cluster()
    auth     = PasswordAuthenticator(user, pw)
    database.authenticate(auth)
    return database

#Connect to specific Couchbase bucket from Couchbase database object
def accessBucket(database, bucket):
    return database.open_bucket(bucket)

#Session Storage High-Level Functions-------------------------------------------
#Move existing session to archives before starting a new live session
def newSession(active, archives, token, query):
    closeExistingSession(active, archives, token)
    storeQuery(active, token, query)

#If session exists in active bucket, move it to archives
def closeExistingSession(active, archives, token):
    doc = retrieveDocument(active,token)
    if doc != []:
        appendDocument(active, token, "cancelled", 1)
        moveDocument(active, archives, token)

#Inialializes user session in couchbase, stores query with timestamp
def storeQuery(bucket, token, query):
    createDocument(bucket, token, query)

#Store symptoms list in user's session
def storeOptions(bucket, token, options):
    appendDocument(bucket, token, "options", options)

#Get symptoms list for user session
def getOptions(bucket, token):
    doc = retrieveDocument(bucket, token)
    return doc['options']

#Stores user's choices from symptoms list, along with timestamp
def storeChoices(bucket, token, choices):
    appendDocument(bucket, token, "choices", choices)
    appendDocument(bucket, token, "choicesTimeStamp", time.createTimestamp())

#Records single user response in feedback list after each question is asked
def storeFeedback(bucket, token, feedback):
    pushNestedList(bucket, token, 'feedback', feedback)

#Migrates live user session to archives
def closeDocument(active, archives, token):
    appendDocument(active, token, "cancelled", 0)
    moveDocument(active, archives, token)

#Couchbase CRUD Low-Level Functions---------------------------------------------
#Initialize an open session in Couchbase once user provides query
def createDocument(bucket, token, query):
    queryTimeStamp = time.createTimestamp()
    #Insert document into couchbase
    bucket.insert(sessionID, {
        "sessionID": time.createSessionID(token, queryTimeStamp),
        "token"    : token,
        "query"    : query,
        "queryTime": queryTimeStamp,
        "feedback" : [],
    })

#Retrive entire user session from bucket based on provided token
def retrieveDocument(bucket, token):
    query = 'SELECT * FROM ' + bucket.bucket + ' WHERE token = $param'
    return queryCouchbase(bucket, query, token)

#Add a field to a document
#NOTE: use only with live bucket, where there is one session per user limit
def appendDocument(bucket, token, field, value):
    #If value is empty or Null, make it 'None' to prevent errors
    if (value == []):
        content = 'None'
    else:
        content = value
    doc = retrieveDocument(bucket, token)
    bucket.mutate_in(doc['sessionID'], sd.insert(field, content))

#Deletes document from bucket based on provided token
def removeDocument(bucket, token):
    doc = retrieveDocument(bucket, token)
    bucket.remove(doc['sessionID'])

#Moves a document from one bucket to another
def moveDocument(source, destination, token):
    doc = retrieveDocument(source, token)
    destination.insert(doc['sessionID'], doc)
    removeDocument(source, token)

#Add an element to an inner list of the document
def pushNestedList(bucket, token, listName, element):
    doc    = retrieveDocument(bucket, token)
    key    = doc['sessionID']
    bucket.mutate_in(key,sd.array_append(listName, element))

#Remove an element at specific index of inner list in document
def popNestedList(bucket, token, listName, index):
    doc          = retrieveDocument(bucket, token)
    key          = doc['sessionID']
    element      = '{0}[{1}]'.format(listName, index)
    bucket.mutate_in(key, sd.remove(element))

#Generic Couchbase Query Function which takes in a query and single variable
def queryCouchbase(bucket, query, param):
    fullQuery = N1QLQuery(query, param=param)
    fullQuery.consistency = CONSISTENCY_REQUEST #Required to 'wait for new docs to be added to index' before querying
    results = bucket.n1ql_query(fullQuery)
    unwrappedResult = [doc[bucket.bucket] for doc in results]
    if unwrappedResult != []:
        unwrappedResult = unwrappedResult[0]
    return unwrappedResult
