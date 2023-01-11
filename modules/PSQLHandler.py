import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import tabulate

'''
The PSQLHandler class, handles the connection to the Postgres SQL server. 
Like the SQSHandler class, it encapsulates and abstracts away the communication with the server and makes it
more manageble. It also helps find bugs by isolating certain operations.
'''
class PSQLHandler:
    def __init__(self, **args):
        self.user = args.get('user', 'postgres')
        self.password = args.get('password', 'postgres')
        self.port = args.get('port', 5432)
        self.dbname = args.get('dbname', 'postgres')
        self.host = args.get('host', 'localhost')
        self.connection = None
        self.db_fields = ["user_id",
                            "device_type",
                            "masked_ip",
                            "masked_device_id",
                            "locale",
                            "app_version",
                            "create_date"]
        self.debug = args.get('debug', 'False')

    # Called to establish connection to server
    def connect(self):
        pg_conn = psycopg2.connect(
            user=self.user,
            password=self.password,
            port=self.port,
            dbname=self.dbname,
            host=self.host
        )
        self.connection = pg_conn

    # Called to disconnect from server
    # Apparently not really needed, but I figured it is good practice
    # To close the connection when done.
    def disconnect(self):
        self.connection.close()

    # Retrieves a connection cursor and returns it.
    def __get_json_cursor(self):
        return self.connection.cursor(cursor_factory=RealDictCursor)

    @staticmethod
    def __execute_and_fetch(cursor, query):
        cursor.execute(query)
        res = cursor.fetchall()
        cursor.close()
        return res

    # When retrieving data from the pqsl data base using psycopg2,
    # it is returned as a realDictRow. This function serves to
    # convert that into a regular python dictionary
    def __RealDictRowToRegularDict(self, realDictRowObject):
        regularDict = {}
        for field in self.db_fields:
            regularDict[field] = str(realDictRowObject[field])
        return regularDict

    # This function is called to get the json response from the server
    # which contains a table, in this case the user_logins table.
    # It is called by the get_user_logins function
    def __get_json_response(self, query):
        cursor = self.__get_json_cursor()
        server_response = self.__execute_and_fetch(cursor, query)
        response = []
        for row in server_response:
            response.append(self.__RealDictRowToRegularDict(row))
        return json.dumps(response)

    # Function used to add a new row to the user_logins table
    def add_user_login(self, data=None):
        cursor = self.__get_json_cursor()
        #This is needed incase the table does not exist to prevent an error
        cursor.execute(""" CREATE TABLE IF NOT EXISTS user_logins(  
                                user_id varchar(128),
                                device_type varchar(32),
                                masked_ip varchar(256),
                                masked_device_id varchar(256),
                                locale varchar(32), 
                                app_version integer,
                                create_date date
                                ); """)

        query = 'INSERT INTO user_logins(user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date) VALUES (%s, %s, %s, %s, %s, %s, TO_DATE(%s,\'YYYYMMDD\'));'
        cursor.execute(query, (data['user_id'], data['device_type'], data['masked_ip'], data["masked_device_id"], data["locale"],
                                str(data["app_version"]).replace(".", ""), str(datetime.today().strftime('%Y%m%d'))))

        self.connection.commit()

    # This prints the sql table as a nice table to the terminal
    def __prettyPrintTable(self, table):
        header = self.db_fields
        rows =  [x.values() for x in table]
        print(tabulate.tabulate(rows, header))
    
    # Retrieves the user_logins table from the sql database and
    # then pretty prints it using the __prettyPrintTable function
    def get_user_logins(self, limit=None):
        query = "SELECT * FROM user_logins;" if limit == None else ("SELECT * FROM user_logins LIMIT " + str(limit) + ";")
        # print("Query chosen: ", query)
        self.__prettyPrintTable(json.loads(self.__get_json_response(query)))