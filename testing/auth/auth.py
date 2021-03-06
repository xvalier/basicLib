import time
import hashlib, uuid
from backend.auth import authSQL as accounts

#Encryption Functions-----------------------------------------------------------
#Generate a unique token based on device ID and timestamp
def generateToken(deviceID):
    combination = deviceID +  str(time.time())
    token = hashlib.md5(combination.encode()).hexdigest()
    return token

#Generate a unique hash based on salt/password combination
def generateHash(password, salt):
    return hashlib.sha512((password+salt).encode()).hexdigest()

#Convert plain text password to salt/hash for access security
def encryptPass(password):
    salt = uuid.uuid4().hex
    hash = generateHash(password, salt)
    return salt, hash

#Validation Functions-----------------------------------------------------------
#Confirm if entered password matches the stored password
def checkPass(connection, name, password):
    passMatch = 0
    storedSalt, storedHash = accounts.getEncryptedPass(connection, name)
    currentHash = generateHash(password, storedSalt)
    if currentHash == storedHash:
        passMatch = 1
    return passMatch

#Check to make user entered all fields in for registration
def checkValidFields(name, password, org, role):
    fieldsValid = 1
    if (name=='') | (password=='') | (org=='') | (role==''):
        fieldsValid = 0
    return fieldsValid
