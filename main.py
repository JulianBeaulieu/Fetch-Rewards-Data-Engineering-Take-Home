from PSQLHandler import PSQLHandler
from SQSHandler import SQSHandler
from Zorro import Zorro

# Create the AWS SQS Queue handler
queue = SQSHandler(debug=True)
queue.connect()

# Create the Postgress SQL Database handler
db = PSQLHandler()
db.connect()

# Create data masking object
zro = Zorro()

# Retrieve a element from the SQS Queue
responses = queue.read_from_AWS_SQS_Queue()

# Mask Data
maskedResponses = zro.mask(responses)

# Add Masked Data to Postgres Server
for maskedResponse in maskedResponses:
    db.add_user_login(maskedResponse)

# Check if server was updated by printing new content
db.get_user_logins()

# Disconnect from servers
queue.disconnect()
db.disconnect()