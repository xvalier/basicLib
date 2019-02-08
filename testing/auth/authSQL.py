from backend.utilities import toolsSQL as sql

#SQL Authentication IO Functions-----------------------------------------------
#Add a new user record into PostgreSQL Users Table
def addUser(connection, name, hash, salt, org, role, token, deviceID):
    sql.createRecord(connection, 'Users', name, hash, salt, org, role, token, deviceID)

#Get token based on user name or deviceID
def getToken(connection, parameter):
    if checkUserExists(connection, parameter):
        attribute = 'name'
    elif checkDeviceExists(connection,parameter):
        attribute = 'deviceID'
    return sql.retrieveRecordContents(connection, 'token', 'Users', attribute, parameter)[0]

#Check if user exists with specified name
def checkUserExists(connection, name):
    return sql.checkRecordExists(connection, 'Users', 'name', name)

#Check if user exists with specified device ID (for automatic login)
def checkDeviceExists(connection, deviceID):
    return sql.checkRecordExists(connection, 'Users', 'deviceID', deviceID)

#Get encrypted salt/hash combo from SQL based on provided name
def getEncryptedPass(connection, name):
    return sql.retrieveRecordContents(connection, 'salt,hash','Users','name',name)
