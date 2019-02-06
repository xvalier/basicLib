import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from backend.helpers import csvHelper as spread
from backend.helpers import psqlHelper as psql
from backend.helpers import esSchema
es = Elasticsearch()
#Change path when switching between server and dev laptop
#path           = '/home/xvalier/Documents/curatedTSG/files/'
path          = '/home/nikilsunilkumar/sets/curatedTSG/files/'
symptomHeader = ['SymId','Description', 'ErrorCode', 'Phrase', 'Keywords']
errorHeader   = ['PLC', 'Motor', 'Camera', 'Antares Camera', 'Cognex Camera', 'Topview Camera',
                'Printer','TIJ','CIJ','TTO','LSR','Zebra','CLM','General','Youtrack','Category', 'Message']

#MAIN ES IMPORT FUNCTION---------------------------------------------------------------------------------
def initialization():
    #Delete previous content and recreate schema
    es.indices.delete(index='errors',ignore=[400,404])
    esSchema.createSchema()
    #Import processed symptoms/errors and upload to ES
    symptoms = spread.importCSV(path+'symptoms.csv')
    #Use [1:] to trim off header
    importElasticsearch(symptoms[1:])

#HELPER FUNCTIONS----------------------------------------------------------------------------------------
#Compose ElasticSearch JSON bulk message for all symptoms, then migrate to ElasticSearch
def importElasticsearch(symptoms):
    tempActions = list(map(addSymptom,symptoms))
    actions = flattenActions(tempActions)
    bulk(es,actions,index='errors',doc_type='symptom', ignore=400)

#Prevent primary/secondary actions from being grouped as a single element in actions list
def flattenActions(actions):
    newActions = []
    for item in actions:
        newActions.append(item[0])
        newActions.append(item[1])
    return newActions

#Convert individual symptom data to JSON format
def addSymptom(symptom):
    actions =[]
    #Add symptom 'key' to JSON (or go to the key if it already exists)
    primaryCommand   = '{"upsert":{"_id":"' + str(symptom[0]) + '","_type" : "_doc", "_index" : "errors"} }'
    actions.append(primaryCommand)
    #Add symptom 'value' to JSON (all its properties)
    secondaryCommand = createPropertiesJSON(symptom)
    actions.append(secondaryCommand)
    return actions

#Convert properties of symptom to JSON format
def createPropertiesJSON(symptom):
    #Add params from symptoms table
    parameters = ''
    for n in range(0,np.size(symptomHeader)):
        entry = ',"'+ symptomHeader[n] + '":"' +str(symptom[n]) + '"'
        parameters = parameters + entry
    #Condense params from errors table into tags (FIGURE OUT LATER), for now just do phrases
    parameters = parameters[1:]                             #Remove initial comma
    secondaryCommand = '{' + parameters + '}'
    return secondaryCommand
