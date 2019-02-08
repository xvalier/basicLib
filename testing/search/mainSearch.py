from backend.search import businesslogicSearch as bl
from backend.utilities import connections.py as link
LOCAL = '/home/xvalier/Documents/curatedTSG/connectLOCAL.ini'
CLOUD = '/home/nikilsunilkumar/sets/curatedTSG/connectCLOUD.ini'

def main(connectionElastic, connectionSQL):
    connectionString = link.chooseConnectionString(CLOUD, LOCAL)
    connections      = link.connectSearch(connectionString)
    addr, port       = link.extractServerGRPCInfo(connectionString)
    display(addr, port, connections)
    bl.serve(addr, port, connections)

def display(addr, port, connections):
    print('Connected Elastic: {0}'.format(connections['elastic']))
    print('Connected Couch: {0}'.format(connections['couchActive']))
    print('Connected Couch: {0}'.format(connections['couchArchives']))
    print('GRPC initialized at {0}:{1}'.format(addr, port))

main()
