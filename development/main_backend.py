import psycopg2
from backend.helpers import readINI as ini
from backend import grpcServer as grpc
from backend.helpers import couchbaseHelper as couch
#Switch connectionStrings between using server and dev laptop
#connectionString  = '/home/xvalier/Documents/curatedTSG/connections2.ini'
connectionString = '/home/nikilsunilkumar/sets/curatedTSG/connections.ini'

def main():
    address, port = ini.readConnectionStringGRPC(connectionString)
    print('Initialized gRPC Server-- IP: '+address+' PORT: '+str(port))
    grpc.serve(port,address)

main()
