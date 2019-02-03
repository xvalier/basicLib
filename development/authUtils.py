import hashlib, uuid
from utilities.database import psqlUtils as psql

#Higher Level Authorization Functions-------------------------------------------
#Register a new user as entry in PSQL Users Table
def addUser(connection, name, hash, salt, org, role, token, deviceID):
    psql.createRecord(connection, 'Users', name, hash, salt, org, role, token, deviceID)

#Get token based on deviceID for autologin
def getTokenFromDevice(connection, devID):
    tokenExists = checkDeviceExists(connection, devID)
    if tokenExists:
        token   = psql.getRecord(connection, 'token', 'users', 'devID', devID)[0]
    return token

#Get token based on user name for normal login
def getTokenFromName(connection, name):
    tokenExists = checkUserExists(connection, name)
    if tokenExists:
        token   = psql.getRecord(connection, 'token', 'users', 'name', name)[0]
    return token

#Check if user exists with specified name
def checkUserExists(connection, name):
    return psql.checkRecordExists(connection, 'users', 'name', name)

#Check if user exists with specified device ID (for automatic login)
def checkDeviceExists(connection, deviceID):
    return psql.checkRecordExists(connection, 'users', 'devID', deviceID)

#Confirm if entered password matches the stored password
def checkPassMatches(name, password):
    passMatch = 0
    storedSalt, storedHash = getEncryptedPassInfo(name)
    currentHash = generateHash(password, storedSalt)
    if currentHash == storedHash:
        passMatch = 1
    return passMatch

#Get encrypted salt/hash combo from SQL based on provided name
def getEncryptedPassInfo(name):
    return psql.getRecord(connection, 'salt,hash','users','name',name)

#Encryption Functions-----------------------------------------------------------
#Convert plain text password to salt/hash for access security
def encryptPass(password):
    salt = uuid.uuid4().hex
    hash = generateHash(password, salt)
    return salt, hash

#Generate a unique token based on device ID and timestamp
def generateToken(deviceID):
    combination = deviceID +  str(time.time())
    token = hashlib.md5(combination.encode()).hexdigest()
    return token

#Generate a unique hash based on salt/password combination
def generateHash(password, salt):
    return hashlib.sha512((password+salt).encode()).hexdigest()

#Check to make user entered all fields in for registration
def checkValidFields(name, password, org, role):
    fieldsValid = 1
    if (name=='') | (password=='') | (org=='') | (role==''):
        fieldsValid = 0
    return fieldsValid
