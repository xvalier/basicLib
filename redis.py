import redis
#REDIS LIVE SESSION FUNCTIONS---------------------------------------------------
#Intialize Redis Usage
def openRedisConnection():
    host, port = ini.readConnectionStringRedis(connectionString)
    connection = redis.Redis(host=host, port=port)
    return connection

def addNode(connection, token, node):
    connection.lpush(token+':live', node)

def removeNode(connection, token, node):
    connection.lpop(token+':live',node)

def removeNodeIndex(connection, token, index):
    connection.lset(token+':live', index, 0)
    connection.lrem(token+':live',1, 0)
