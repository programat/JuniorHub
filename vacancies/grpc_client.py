import grpc
import internship_pb2
import internship_pb2_grpc

def get_internships():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = internship_pb2_grpc.InternshipServiceStub(channel)
        request = internship_pb2.GetInternshipsRequest()
        response = stub.GetInternships(request)
        return response.categories
