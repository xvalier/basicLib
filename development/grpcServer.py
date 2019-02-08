from concurrent import futures
from operator import itemgetter
import time
import grpc
from proto import sets_pb2
from proto import sets_pb2_grpc
from backend.helpers import esQuery
from backend.businesslogic import Session
from backend.helpers import authHelper as auth
from backend.helpers import couchbaseHelper as couch

#gRPC Server Initialization
def serve(cs, port, address):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sets_pb2_grpc.add_ErrorResolutionServicer_to_server(ErrorResolutionServicer(cs), server)
    server.add_insecure_port('%s:%d' % (address, port))
    server.start()
    try:
        while True:
            time.sleep(60*60*24)
    except KeyboardInterrupt:
        server.stop(0)

class ErrorResolutionServicer(sets_pb2_grpc.ErrorResolutionServicer):
    def __init__(cs):
        connectionString = cs
        
    connectionString = cs
    #Internal attributes
    sessions      = {}
    active        = couch.openCouchbaseConnection()[0]
    archives      = couch.openCouchbaseConnection()[1]

    #Takes in user information to register a new user, sends back user's session token
    def createLogin(self, request, context):
        message     = ''
        successFlag = 0
        token       = ''
        #Extract information from gRPC message, validate the response
        name     = request.email
        password = request.password
        org      = request.organization
        role     = request.role
        did      = request.devID
        #If fields are missing or invalid, send error message
        if (auth.validateRegFields(name, password, org, role)):
            #If user name exists, send error message
            if (auth.findUser(name)):
                message = 'User is already registered'
                print(message)
            else:
                #Generate encrypted pass information, generate user token for device
                salt, hash   = auth.encryptPass(password)
                token        = auth.generateToken(did)
                #Add all user info to SQL Users Table
                auth.addUser(name, hash, salt, org, role, token, did)
                successFlag = 1
        else:
            message = 'Some fields are not filled in, or were invalid. Please correct this.'
        #Encapsulate receipt with results, send back to frontend
        receipt = sets_pb2.Receipt(
            message     = message,
            successFlag = successFlag,
            token       = token
        )
        return receipt

    #Validate user login information, send back token if successful
    def sendLogin(self, request, context):
        message     = ''
        successFlag = 0
        token       = ''
        #Check if user already exists, send error message
        if not (auth.findUser(request.email)):
            message = 'User does not exist'
            #Check if password matches user
            if not (auth.verifyPass(request.email, request.password)):
                message = 'Invalid password was provided'
            else:
                token = auth.getToken(request.email)
                successFlag = 1
        #Encapsulate receipt with results, send back to frontend
        receipt = sets_pb2.Receipt(
            message     = message,
            successFlag = successFlag,
            token       = token
        )
        return receipt

    def automaticLogin(self, request, context):
        message     = ''
        successFlag = 0
        token       = ''
        #Extract device id, check if it matches existing user, return token if it does
        deviceID   = request.devID
        token      = auth.getToken(deviceID)
        #Create error message if token was not generated
        if token == '':
            message = 'Device is not registered to an existing user. Please register to auto-login'
        else:
            successFlag = 1
        #Encapsulate receipt with results, send back to frontend
        receipt = sets_pb2.Receipt(
            message     = message,
            successFlag = successFlag,
            token       = token
        )
        return receipt

    #Takes in user text query, sends back a list of relevant symptoms
    def getSymptomList(self, request, context):
        self.active    = couch.openCouchbaseConnection()[0]
        self.archives = couch.openCouchbaseConnection()[1]
        #De-encapsulate query, process it to get symptomsList, store as attribute
        couch.closeExistingSession(self.active, self.archives, request.token)
        couch.storeQuery(self.active, request.token, request.input)
        symptomsList = processQuery(request.input)
        couch.storeOptions(self.active, request.token, symptomsList)
        #Encapsulate as gRPC symptom, then send to frontend as gRPC ServerList message
        tempList = []
        for n in range(0,len(symptomsList)):
            description = symptomsList[n][2].replace("...","\r\n")
            tempList.append(sets_pb2.Symptom(input=description))
        serverList = sets_pb2.ServerList(symptoms = tempList)
        return serverList

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
#Takes in user text query, returns list of relevant symptoms from ElasticSearch
def processQuery(userQuery):
    #Get results from ElasticSearch
    result = esQuery.searchDatabase(userQuery)
    #Convert raw ElasticSearch results into a usable list
    unwrappedResult = result['hits']['hits']
    symptoms = [[entry['_source']['SymId'],
                entry['_score'],
                entry['_source']['Description']] for entry in unwrappedResult]
    return symptoms

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
