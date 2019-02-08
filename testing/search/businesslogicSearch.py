from concurrent import futures
import time
import grpc
from backend.proto import sets_pb2
from backend.proto import sets_pb2_grpc
from backend.utilities import toolsElastic as search
from backend.utilities import toolsCouch as session

#Service Definition-------------------------------------------------------------
class SearchServicer(sets_pb2_grpc.SearchServicer):
    def __init__(connections):
        self.search        = connections['elastic']
        self.liveSessions  = connections['couchActive']
        self.oldSessions   = connections['couchArchives']

    search, liveSessions, oldSessions   = ''

    #Search/return symptoms that match user query description
    def getSymptomList(self, request, context):
        query, token = unwrapUserQuery(request)
        session.newSession(self.liveSessions. self.oldSessions, token, query)
        relevantSymptoms = processQuery(self.search, query)
        session.storeOptions(self.liveSessions, token, relevantSymptoms)
        message = wrapSymptomsList(relevantSymptoms)
        return message

#Preprocessing Helpers----------------------------------------------------------
#Process user query through ElasticSearch and return most relevant symptoms
def processQuery(connection, query):
    results = search.executeQuery(connection, query)
    return unwrapElasticResults(results)

#Process ElasticSearch list into a readable symptoms dict
def unwrapElasticResults(results):
    symptomList = []
    unwrappedResults = results['hits']['hits']
    for entry in unwrappedResult:
        symptom = {
            "id":          entry['_source']['id'],
            "score":       entry['_score'],
            "description": entry['_source']['description']
        }
        symptomList.append(symptom)
    return symptomsList

#GRPC Functions-----------------------------------------------------------------
#De-encapsulate gRPC message attributes
def unwrapUserQuery(message):
    return message.query, message.token

#Encapsulate full symptoms list as a gRPC message
def wrapSymptomsList(symptomsList):
    symList = []
    for symptom in symptomsList:
        symptomMessage = wrapSymptom(symptom)
        symList.append(symptomMessage)
    message = sets_pb2.SymptomsList(symptoms = symList)
    return message

#Encapsulate individual symptom descriptions into gRPC messages
def wrapSymptom(symptom):
    description = symptom['description'].replace("...","\r\n")
    message = sets_pb2.Symptom(description=description)
    return message

#Initializes Search Microservice as a GRPC service
def serve(address, port, connections):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sets_pb2_grpc.add_SearchServicer_to_server(SearchServicer(connections), server)
    server.add_insecure_port('%s:%d' % (address, port))
    server.start()
    try:
        while True:
            time.sleep(60*60*24)
    except KeyboardInterrupt:
        server.stop(0)
