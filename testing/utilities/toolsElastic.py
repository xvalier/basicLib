from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from backend.schema import schemaElastic
from backend.utilities import toolsCSV as spread
symptomHeader = ['id','description', 'errCode', 'phrase', 'keywords']

#Connection Functions-----------------------------------------------------------
#Connect to ElasticSearch Search Engine
def accessElastic():
    return Elasticsearch()

#COMPOSITE FUNCTIONS------------------------------------------------------------
def importProcedure(connection, csvPath):
    deleteAllDocuments(connection)
    createSchema(connection)
    symptoms = spread.importCSV(csvPath+'symptoms.csv')
    bulkFillDocuments(commands, symptoms[1:])

#CORE FUNCTIONS-----------------------------------------------------------------
#Connect to PostgreSQL Database via Credentials
def accessElastic():
    return ElasticSearch();

#Obtain most relevant indexed documents based on query
def executeQuery(connection, description):
    query = schemaElastic.compileQuery(description)
    return connection.search(index='errors', doc_type='symptom', body=query)

#Create schema for filter/analyzer settings prior to adding documents to index
def createSchema(connection):
    settings = schemaElastic.compileIndex()
    connection.indices.create(index='errors', body = settings)

#Deletes all documents stored in index
def deleteAllDocuments(connection):
    connection.indices.delete(index='errors',ignore=[400,404])

#CSV IMPORT/EXPORT FUNCTIONS----------------------------------------------------
#Compose ElasticSearch JSON bulk message for all symptoms, then migrate to ElasticSearch
def bulkFillDocuments(connection, symptoms):
    rawCommands = list(map(addSymptomDocument,symptoms))
    commands = flattenCommands(rawCommands)
    bulk(connection,commands,index='errors',doc_type='symptom', ignore=400)

#Prevent primary/secondary actions from being grouped as a single element in actions list
def flattenActions(commands):
    newCommands = []
    for item in commands:
        newCommands.append(item[0])
        newCommands.append(item[1])
    return newCommands

#Convert symptom record into a JSON Document
def createSymptomDocument(symptom):
    commands =[]
    commands.append(createDocumentKey(symptom[0]))
    commands.append(createDocumentValue(symptom))
    return commands

#Parse symptom id to set document key
def createDocumentKey(id):
    docKey = '{"upsert":{"_id":"{0}","_type" : "_doc", "_index" : "errors"} }'
    return docKey.format(str(id))

#Parse all symptom properties to set document content
def createDocumentValue(symptom):
    parameters = ''
    #Add each setting to document value one at a time
    for index in range(0,len(symptomHeader)):
        parameter = symptomHeader[index]
        value     = str(symptom[index])
        setting = ',"{0}":"{1}"'.format(parameter, value)
        parameters = parameters + setting
    #Remove initial comma and format as secondary command
    parameters = parameters[1:]
    return '{{0}}'.format(parameters)
