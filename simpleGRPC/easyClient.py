import grpc
import easy_pb2
import easy_pb2_grpc
port = 4040
address = 'localhost'

def main():
    stubber = stub(port, address)
    while(1):
        request = input('What do you want to say:')
        message = easy_pb2.clientMSG(request=request)
        response=stubber.easyCall(message)
        print(response.response)

#Client gRPC Initilization
def stub(port, address):
    channel = grpc.insecure_channel('%s:%d' % (address, port))
    stub    = easy_pb2_grpc.easyServiceStub(channel)
    return stub

main()
