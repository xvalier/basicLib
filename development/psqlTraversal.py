from utilities.database import psqlUtils as psql

#Retrieve description/precision values based on node id
def getNodeProperties(connection, id, type):
    if type = 'symptoms':
        returnClause = 'description,precision'
        attribute    = 'symId'
        edges        = getErrorIdsForward(connection, id)
    elif type = 'resolutions':
        returnClause = 'description'
        attribute    = 'resId'
        edges        = getErrorIdsBackward(connection, id)
    properties  = psql.getRecord(connection, returnClause, type, attribute, id)
    return properties, edges

def getErrorIdsForward(connection, symId):
    return psql.getRecord(connection, 'errorId','map_s2e','symId', symId)

def getErrorIdsBackward(connection, resId):
    return psql.getRecord(connection, 'errorId','resolutions','resId', resId)

def getResIds(connection, errorId):
    return psql.getRecord(connection, 'resId','resolutions','errorId', errorId)

def getSymIds(connection, errorId):
    return psql.getRecord(connection, 'symId','map_s2e','errorId', errorId)
