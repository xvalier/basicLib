from concurrent import futures
import time
import grpc
import easy_pb2
import easy_pb2_grpc
port = 4040
address = 'localhost'

def main():
    testAdditionalParam = 'test--'
    print('Serving at {0}:{1}'.format(address,port))
    serve(testAdditionalParam, port, address)

#gRPC Server Initialization
def serve(connection, port, address):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    easy_pb2_grpc.add_easyServiceServicer_to_server(easyServiceServicer(testAdditionalParam), server)
    server.add_insecure_port('%s:%d' % (address, port))
    server.start()
    try:
        while True:
            time.sleep(60*60*24)
    except KeyboardInterrupt:
        server.stop(0)

class easyServiceServicer(easy_pb2_grpc.easyServiceServicer):
    def __init__(self,testAdditionalParam):
        self.test = testAdditionalParam
    test = ''
    def easyCall(self, request, context):
        a = self.connection + request.request
        print(a)
        return easy_pb2.serverMSG(response=a)

main()
