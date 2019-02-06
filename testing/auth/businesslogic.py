from concurrent import futures
import time
import grpc
from proto import authentication_pb2
from proto import authentication_pb2_grpc
from backend.auth import auth
from backend.auth import authSQL

#GRPC Server Initialization
def serve(port, address, connection):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sets_pb2_grpc.add_ErrorResolutionServicer_to_server(AuthenticationServicer(connection), server)
    server.add_insecure_port('%s:%d' % (address, port))
    server.start()
    try:
        while True:
            time.sleep(60*60*24)
    except KeyboardInterrupt:
        server.stop(0)

class AuthenticationServicer(sets_pb2_grpc.AuthenticationServicer, connection):
    def __init__:
        self.connection = connection

    #Internal attibute for PSQL Connection
    connection = ''

    #Register new user from provided credentials, give back token
    def registerLogin(self, request, context):
        msg     = ''
        success = 0
        token   = ''
        #If fields are valid and name not already taken, create user
        if (auth.checkValidFields(self.connection, name, password, org, role)):
            if not (psqAuth.checkUserExists(self.connection, name)):
                token      = auth.generateToken(request.deviceID)
                salt, hash = auth.encryptPass(request.password)
                authSQL.addUser(self.connection,
                    request.name,
                    request.hash,
                    request.salt,
                    request.organization,
                    request.role,
                    request.deviceID
                )
                success = 1
                token = authSQL.getToken(self.connection, request.name)
            else:
                msg = 'User is already registered'
        else:
            msg = 'Some fields are not filled in, or were invalid. Please correct this.'
        #Encapsulate receipt with results, send back to frontend
        return sets_pb2.Receipt(message=msg,successFlag=success,token=token)

    #Validate user login information, send back token if successful
    def normalLogin(self, request, context):
        msg     = ''
        success = 0
        token   = ''
        #Extract credentials from grpc message
        name        = request.name
        pw          = request.password
        #If user exists and pass is correct, get token
        if (authSQL.checkUserExists(self.connection, name)):
            if (auth.checkPass(self.connection, name, pw)):
                token = authSQL.getToken(self.connection, name)
                success = 1
            else:
                msg = 'Invalid Password was provided'
        else:
            msg = 'User does not exist'
        #Encapsulate receipt with results, send back to frontend
        return sets_pb2.Receipt(message=msg,successFlag=success,token=token)

    #If device is registed in any user on database, send back token
    def automaticLogin(self, request, context):
        msg     = ''
        success = 0
        token   = ''
        #Extract credentials from grpc message
        deviceID   = request.devID
        #If device is already registed, get token
        if (authSQL.checkDeviceExists(self.connection, deviceID)):
            token   = authSQL.getToken(self.connection, deviceID)
            success = 1
        else:
            msg = 'Device is not registered to an existing user. Please register to auto-login'
        #Encapsulate receipt with results, send back to frontend
        return sets_pb2.Receipt(message=msg,successFlag=success,token=token)
