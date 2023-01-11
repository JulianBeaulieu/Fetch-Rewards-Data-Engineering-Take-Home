import math

'''
I named this object Zorro, because it masks identities. I know, not quite like Zorro,
but he was masked and so I thought this was a fun nudge.
'''
class Zorro:
    def __init__(self):
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

    def __encrypt(self, value):
        value = str(value)
        return int.from_bytes(value.encode(), 'little')

    def __maskMultiple(self, serverResponses):
        return [self.__maskSingle(response) for response in serverResponses]

    def  __maskSingle(self, serverResponse):
        masked_response = {}

        for field in self.queue_fields:
            if(self.MASKED in self.bridge[field]):
                masked_response[self.bridge[field]] = self.__encrypt(serverResponse[field])  
            else:
                masked_response[self.bridge[field]] = serverResponse[field]
        
        return masked_response


    def mask(self, serverResponses):
        if(type(serverResponses) is "list"):
            return self.__maskMultiple(serverResponses)
        else:
            return self.__maskMultiple(serverResponses)