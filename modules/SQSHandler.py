import boto3
from botocore import UNSIGNED
from botocore.client import Config
import json

'''
The SQSHandler class, handles the connection to the AWS SQS Queue server. 
It encapsulates and abstracts away the communication with the server and makes it
more manageble. It also helps find bugs by isolating certain operations.
'''
class SQSHandler:
    def __init__(self, debug=False):
        self.AWS_REGION = 'us-east-1'
        self.QUEUE_URL = 'http://localhost:4566/000000000000/login-queue'
        self.sqs = None
        self.debug = debug

    # Called to establish connection to server
    def connect(self):
        # Create an SQS client
        self.sqs = boto3.client('sqs', 
                                endpoint_url=self.QUEUE_URL, 
                                region_name=self.AWS_REGION, 
                                config=Config(signature_version=UNSIGNED))

    # Called to disconnect from server
    def disconnect(self):
        self.sqs.close()

    # This function essentially 'pops' the front of the queue
    def __delete_from_AWS_SQS_Queue(self, handles):
        for handle in handles:
            response = self.sqs.delete_message( QueueUrl=self.QUEUE_URL,
                                                ReceiptHandle=handle )
            if(self.debug):
                print("\nDeleting Response in Queue:\n", response)

    # This function reads or 'peaks' onto the queue and retrieves the objects.
    # It also calls the 'pop' function to delete the object on the front of the queue
    def read_from_AWS_SQS_Queue(self):
        # Receive a message from the queue
        response = self.sqs.receive_message(
            QueueUrl=self.QUEUE_URL,
            AttributeNames=['All'],
            MaxNumberOfMessages=100,
            WaitTimeSeconds=0
        )

        # Print the message body
        if(self.debug):
            print("\nResponse from Queue:\n", response)

        messages = []
        handles = []

        if(not("Messages" in response)):
            return None

        for message in response['Messages']:
            handles.append(message["ReceiptHandle"])
            messages.append(json.loads(message['Body']))

        self.__delete_from_AWS_SQS_Queue(handles)

        return messages