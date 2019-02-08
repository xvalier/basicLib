from backend.search import businesslogicAuth as bl
from backend.utilities import connections.py as link
LOCAL = '/home/xvalier/Documents/curatedTSG/connectLOCAL.ini'
CLOUD = '/home/nikilsunilkumar/sets/curatedTSG/connectCLOUD.ini'

def main():
    connectionString = link.chooseConnectionString(CLOUD, LOCAL)
    connections      = link.connectTraversal(connectionString)
    addr, port       = link.extractServerGRPCInfo(connectionString)
    display(addr, port, connections)
    bl.serve(addr, port, connections)

def display(addr, port, connections):
    print('Connected PSQL: {0}'.format(connections['psql']))
    print('Connected Couch: {0}'.format(connections['couchActive']))
    print('Connected Couch: {0}'.format(connections['couchArchives']))
    print('GRPC initialized at {0}:{1}'.format(addr, port))

main()
