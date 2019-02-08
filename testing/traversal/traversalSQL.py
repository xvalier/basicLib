from backend.utilities import toolsSQL as sql

#Retrieve description/precision values based on node id
def getNodeProperties(connection, id, type):
    if type = 'symptoms':
        returnClause = 'description,precision'
        edges        = getErrorIdsForward(connection, id)
    elif type = 'resolutions':
        returnClause = 'description'
        edges        = getErrorIdsBackward(connection, id)
    properties  = sql.retriveRecordContents(connection, returnClause, type, 'id', id)
    return properties, edges

def getErrorIdsForward(connection, symId):
    return sql.retrieveRecordContents(connection, 'errorId','Sym_Err','symId', symId)

def getErrorIdsBackward(connection, resId):
    return sql.retrieveRecordContents(connection, 'errorId','Resolutions','id', resId)

def getResIds(connection, errorId):
    return sql.retrieveRecordContents(connection, 'id','Resolutions','errorId', errorId)

def getSymIds(connection, errorId):
    return sql.retrieveRecordContents(connection, 'symId','Sym_Err','errorId', errorId)
