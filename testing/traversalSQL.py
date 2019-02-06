from backend.utilities import toolsSQL as psql

#Retrieve description/precision values based on node id
def getNodeProperties(connection, id, type):
    if type = 'symptoms':
        returnClause = 'description,precision'
        edges        = getErrorIdsForward(connection, id)
    elif type = 'resolutions':
        returnClause = 'description'
        edges        = getErrorIdsBackward(connection, id)
    properties  = psql.retriveRecordContents(connection, returnClause, type, 'id', id)
    return properties, edges

def getErrorIdsForward(connection, symId):
    return psql.retrieveRecordContents(connection, 'errorId','Sym_Err','symId', symId)

def getErrorIdsBackward(connection, resId):
    return psql.retrieveRecordContents(connection, 'errorId','Resolutions','id', resId)

def getResIds(connection, errorId):
    return psql.retrieveRecordContents(connection, 'id','Resolutions','errorId', errorId)

def getSymIds(connection, errorId):
    return psql.retrieveRecordContents(connection, 'symId','Sym_Err','errorId', errorId)
