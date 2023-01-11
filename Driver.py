from modules.PSQLHandler import PSQLHandler
from modules.SQSHandler import SQSHandler
from modules.Zorro import Zorro

# Create the AWS SQS Queue handler
queue = SQSHandler()
queue.connect()

# Create the Postgress SQL Database handler
db = PSQLHandler()
db.connect()

# Create data masking object
zro = Zorro()

print("Running Program...\nTo stop program, press any key.")

running = True
while running:
    try:
        # Retrieve a element from the SQS Queue
        responses = queue.read_from_AWS_SQS_Queue()

        # If the response object is None (null) then the data in 
        # the queue was wrong/corrupt and we will be skipping it
        if(responses == None):
            running = False
            continue

        # Mask Data
        maskedResponses = zro.mask(responses)

        # Add Masked Data to Postgres Server
        for maskedResponse in maskedResponses:
            db.add_user_login(maskedResponse)

    # Checks if keyboard interrupt happened
    except KeyboardInterrupt:
        print("Stopping loop due to keyboard interrupt")
        running = False

# Simply allows user to see table in Postgres server after all of the additions
var = input("Would you like to see the current Postgres Database? Y/N ")
if("y" in var.lower()):
    # Check if server was updated by printing new content
    db.get_user_logins()

# Disconnect from servers
queue.disconnect()
db.disconnect()