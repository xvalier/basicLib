from concurrent import futures
from operator import itemgetter
import time
import grpc
from proto import sets_pb2
from proto import sets_pb2_grpc
from backend.traversal.businesslogicTraversal import Tree
from backend.utilities import traversalSQL as graph
from backend.utilities import toolsCouch as session

class TraversalServicer(sets_pb2_grpc.TraversalServicer):
    def __init__(connections):
        self.database = connections['psql']
        self.liveSessions  = connections['couchActive']
        self.oldSessions   = connections['couchArchives']

    database, liveSessions, oldSessions = ''
    sessions = {}

    #Takes in user selection (list of bools), sends back first question to ask
    def startSession(self, request, context):
        #De-encapsulate selection, trims symList based on selection, create Session
        choices  = request.input
        token    = request.token
        couch.storeChoices(self.active, token, choices)
        symList      = couch.getOptions(self.active, token)
        filteredSyms = filterSymptoms(symList, choices)
        self.sessions[token] = Session(filteredSyms)
        #Send gRPC ServerFeedback message to frontend with next question to ask
        currentSession = self.sessions[token]
        if len(currentSession.tree) > 0:
            question       = currentSession.nextQuestion()
            serverFeedback = sets_pb2.ServerFeedback(input=question, doneFlag=0,solvedFlag=0)
        #If no symptoms, close the session
        else:
            serverFeedback = self.endSession(token, currentSession.solvedFlag)
        return serverFeedback

    #Takes in user feedback (yes/no), sends back next question to ask
    def getNextQuestion(self, request, context):
        token          = request.token
        currentSession = self.sessions[token]
        #Record response in document
        askedQuestion  = currentSession.tree[0]
        feedback = {
            'id'         : askedQuestion.id,
            'description': askedQuestion.description,
            'type'       : askedQuestion.type,
            'score'      : str(askedQuestion.score),
            'response'   : str(request.input),
            'timestamp'  : couch.createTimestamp()
        }
        couch.storeFeedback(self.active, token, feedback)
        #De-encapsulate user feedback, process session to continue tranversal
        currentSession.processResponse(request.input)
        #Send gRPC ServerFeedback message to frontend with next question to ask
        if (currentSession.doneFlag == 0) & (len(currentSession.tree)>0):
            feedback = currentSession.nextQuestion()
            serverFeedback = sets_pb2.ServerFeedback(input = feedback, doneFlag=0, solvedFlag=0)
        #If no more symptoms (or if resolved), close the session
        else:
            serverFeedback = self.endSession(token, currentSession.solvedFlag)
        return serverFeedback

    #Procedure to close sessions
    def endSession(self,token, solvedFlag):
        #Remove current user session from active sessions
        couch.closeDocument(self.active, self.archives, token)
        self.sessions.pop(token)
        #Return appropiate message to frontend based on if issue was resolved
        if solvedFlag == 1:
            feedback = 'The issue has been resolved! Have a good day!'
        else:
            feedback = 'The issue you have described was not documented in our records. Please contact AfterSales'
        serverFeedback = sets_pb2.ServerFeedback(input = feedback, doneFlag=1, solvedFlag=solvedFlag)
        return serverFeedback

#Preprocessing Helpers----------------------------------------------------------
#Trims list of symptoms based on user feedback
def filterSymptoms(symptomsList, feedback):
    #Convert feedback string into a list of strings
    feedbackList = []
    for char in feedback:
        feedbackList.append(char)
    #Trim list of symptoms
    parsedSymptoms = []
    for n in feedbackList:
        parsedSymptoms.append(symptomsList[int(n)])
    #Sort trimmed list
    parsedSymptoms = sorted(parsedSymptoms, key = itemgetter(1), reverse = True)
    return parsedSymptoms

#GRPC Functions-----------------------------------------------------------------
#gRPC Server Initialization
def serve(port, address, connections):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sets_pb2_grpc.add_TraversalServicer_to_server(TraversalServicer(connections), server)
    server.add_insecure_port('%s:%d' % (address, port))
    server.start()
    try:
        while True:
            time.sleep(60*60*24)
    except KeyboardInterrupt:
        server.stop(0)
