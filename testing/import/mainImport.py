from backend.utilities import connections.py as link
from backend.utilities import toolsElastic as search
from backend.import import importSQL as sql
LOCAL = '/home/xvalier/Documents/curatedTSG/connectLOCAL.ini'
CLOUD = '/home/nikilsunilkumar/sets/curatedTSG/connectCLOUD.ini'

def main(connectionElastic, connectionSQL):
    connectionString = link.chooseConnectionString(CLOUD, LOCAL)
    connections      = link.connectImport(connectionString)
    display(addr, port, connections)
    trigger = input('Type "i" to import content from csv:')
    if (trigger== "i"):
        updateGraph(connections)

def display(addr, port, connections):
    print('Connected Elastic: {0}'.format(connections['elastic']))
    print('Connected PSQL: {0}'.format(connections['psql']))

def uploadGraph(connections):
    sql.importProcedure(connections['sql'], connections['csv'])
    print('SQL Database has been updated...')
    search.importProcedure(connections['elastic'], connections['csv'])
    print('Search Engine has been updated...')

main()
