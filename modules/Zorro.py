import math
import hashlib

'''
I named this object Zorro, because it masks identities. I know, not quite like Zorro,
but he was masked and so I thought this was a fun nudge.
'''
class Zorro:
    def __init__(self, encryptionType=0, debug=False):
        self.queue_fields = ["user_id",
                                "app_version", 
                                "device_type", 
                                "ip", 
                                "locale", 
                                "device_id"]

        self.db_fields = ["user_id",
                            "device_type",
                            "masked_ip",
                            "masked_device_id",
                            "locale",
                            "app_version"]

        self.bridge = {"user_id": "user_id",
                        "app_version": "app_version",
                        "device_type": "device_type",
                        "locale": "locale",
                        "ip": "masked_ip",
                        "device_id": "masked_device_id",}

        self.MASKED = "masked"
        self.debug = debug
        self.encryptionType = encryptionType

    # This is the actual encryption method, it takes in an object
    # and then encrypts/masks it. 
    # Encryption type 0 is reversable
    # Encryption type 1 is NOT easily reversable without knowing the input
    # Encryption type ELSE is just the input value as a string
    def __encrypt(self, value):
        value = str(value)
        if(self.encryptionType == 0):
            return int.from_bytes(value.encode(), 'little')
        elif(self.encryptionType == 1):
            return hashlib.sha256(value.encode()).hexdigest()
        else: 
            return value

    # Function which encrypts all the responses. Skips ones wich are of the None type
    def __maskMultiple(self, serverResponses):
        return [self.__maskSingle(response) for response in serverResponses if self.__maskSingle(response) is not None]

    # This function tries to convert the objects/jsons from the SQS server to objects for the Postgres server
    # Fiels which need masking are masked.
    def  __maskSingle(self, serverResponse):
        try:
            masked_response = {}
            for field in self.queue_fields:
                if(self.debug):
                    print(field, serverResponse)
                if(self.MASKED in self.bridge[field]):
                    masked_response[self.bridge[field]] = self.__encrypt(serverResponse[field])  
                else:
                    masked_response[self.bridge[field]] = serverResponse[field]
            
            return masked_response
        except KeyError as keyexception:
            if(self.debug):
                print(field, serverResponse)
                print(keyexception)
            return None

    # This is the wrapper function. Incase the incoming object is not a list,
    # it can dynamically switch between lists of objects or just a single object.
    # Keeps the code more flexible to prevent issues.
    def mask(self, serverResponses):
        if(type(serverResponses) == "list"):
            return self.__maskMultiple(serverResponses)
        else:
            return self.__maskMultiple(serverResponses)