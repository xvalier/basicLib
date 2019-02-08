from concurrent import futures
import time
import grpc
from proto import sets_pb2
from proto import sets_pb2_grpc
from backend.auth import auth
from backend.auth import authSQL as accounts

class AuthServicer(sets_pb2_grpc.AuthServicer):
    def __init__(connections):
        self.database = connections['psql']
    database = ''

    #Register new user from provided credentials, give back token
    def registerLogin(self, request, context):
        msg, success, token = ''
        #If fields are valid and name not already taken, create user
        if (auth.checkValidFields(self.database, name, password, org, role)):
            if not (accounts.checkUserExists(self.database, name)):
                token      = auth.generateToken(request.deviceID)
                salt, hash = auth.encryptPass(request.password)
                accounts.addUser(self.database,
                    request.name,
                    request.hash,
                    request.salt,
                    request.organization,
                    request.role,
                    request.deviceID
                )
                success = 1
                token = accounts.getToken(self.database, request.name)
            else:
                msg = 'User is already registered'
        else:
            msg = 'Some fields are not filled in, or were invalid. Please correct this.'
        return wrapReceipt(msg, success, token)

    #Validate user login information, send back token if successful
    def normalLogin(self, request, context):
        msg, success, token = ''
        name        = request.name
        pw          = request.password
        #If user exists and pass is correct, get token
        if (accounts.checkUserExists(self.database, name)):
            if (auth.checkPass(self.database, name, pw)):
                token = accounts.getToken(self.database, name)
                success = 1
            else:
                msg = 'Invalid Password was provided'
        else:
            msg = 'User does not exist'
        #Encapsulate receipt with results, send back to frontend
        return wrapReceipt(msg, success, token)

    #If device is registed in any user on database, send back token
    def automaticLogin(self, request, context):
        msg, success, token = ''
        deviceID   = request.devID
        #If device is already registed, get token
        if (accounts.checkDeviceExists(self.database, deviceID)):
            token   = accounts.getToken(self.database, deviceID)
            success = 1
        else:
            msg = 'Device is not registered to an existing user. Please register to auto-login'
        #Encapsulate receipt with results, send back to frontend
        return wrapReceipt(msg, success, token)

#GRPC Functions-----------------------------------------------------------------
#Encapsulate receipt contents into grpc message
def wrapReceipt(message, success, token):
    sets_pb2.Receipt(message=message,successFlag=success,token=token)

#GRPC Server Initialization
def serve(port, address, connection):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sets_pb2_grpc.add_AuthServicer_to_server(AuthServicer(connections), server)
    server.add_insecure_port('%s:%d' % (address, port))
    server.start()
    try:
        while True:
            time.sleep(60*60*24)
    except KeyboardInterrupt:
        server.stop(0)
