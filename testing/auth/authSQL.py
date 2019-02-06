from backend.utilities import toolsSQL as psql

#SQL Authentication IO Functions-----------------------------------------------
#Add a new user record into PostgreSQL Users Table
def addUser(connection, name, hash, salt, org, role, token, deviceID):
    psql.createRecord(connection, 'Users', name, hash, salt, org, role, token, deviceID)

#Get token based on user name or deviceID
def getToken(connection, parameter):
    if checkUserExists(connection, parameter):
        attribute = 'name'
    elif checkDeviceExists(connection,parameter):
        attribute = 'deviceID'
    return psql.retrieveRecordContents(connection, 'token', 'Users', attribute, parameter)[0]

#Check if user exists with specified name
def checkUserExists(connection, name):
    return psql.checkRecordExists(connection, 'Users', 'name', name)

#Check if user exists with specified device ID (for automatic login)
def checkDeviceExists(connection, deviceID):
    return psql.checkRecordExists(connection, 'Users', 'deviceID', deviceID)

#Get encrypted salt/hash combo from SQL based on provided name
def getEncryptedPass(connection, name):
    return psql.retrieveRecordContents(connection, 'salt,hash','Users','name',name)
