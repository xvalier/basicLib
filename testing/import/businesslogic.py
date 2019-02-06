from backend.import import importSQL as sql
from backend.utilities import toolsElastic as es

def uploadGraph(connectionElastic, connectionSQL, csvPath):
    sql.importProcedure(connectionSQL, csvPath)
    es.importProcedure(connectionElastic, csvPath)
