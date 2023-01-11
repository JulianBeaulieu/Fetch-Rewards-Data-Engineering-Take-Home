import boto3
from botocore import UNSIGNED
from botocore.client import Config
import json

class SQSHandler:
    def __init__(self, debug=False):
        self.AWS_REGION = 'us-east-1'
        self.QUEUE_URL = 'http://localhost:4566/000000000000/login-queue'
        self.sqs = None
        self.debug = debug

    def connect(self):
        # Create an SQS client
        self.sqs = boto3.client('sqs', 
                                endpoint_url=self.QUEUE_URL, 
                                region_name=self.AWS_REGION, 
                                config=Config(signature_version=UNSIGNED))

    def disconnect(self):
        self.sqs.close()

    def __delete_from_AWS_SQS_Queue(self, handles):
        for handle in handles:
            response = self.sqs.delete_message( QueueUrl=self.QUEUE_URL,
                                                ReceiptHandle=handle )
            print(response)

    def read_from_AWS_SQS_Queue(self):
        # Receive a message from the queue
        response = self.sqs.receive_message(
            QueueUrl=self.QUEUE_URL,
            AttributeNames=['All'],
            # MaxNumberOfMessages=1,
            WaitTimeSeconds=0
        )

        # Print the message body
        if(self.debug):
            print(response)

        messages = []
        handles = []
        
        for message in response['Messages']:
            handles.append(message["ReceiptHandle"])
            messages.append(json.loads(message['Body']))

        print("\n\n")
        self.__delete_from_AWS_SQS_Queue(handles)

        return messages