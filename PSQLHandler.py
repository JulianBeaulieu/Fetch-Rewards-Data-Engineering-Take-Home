import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import tabulate

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

    def connect(self):
        pg_conn = psycopg2.connect(
            user=self.user,
            password=self.password,
            port=self.port,
            dbname=self.dbname,
            host=self.host
        )
        self.connection = pg_conn

    def disconnect(self):
        self.connection.close()

    def get_json_cursor(self):
        return self.connection.cursor(cursor_factory=RealDictCursor)

    @staticmethod
    def execute_and_fetch(cursor, query):
        cursor.execute(query)
        res = cursor.fetchall()
        cursor.close()
        return res

    def __RealDictRowToRegularDict(self, realDictRowObject):
        regularDict = {}
        for field in self.db_fields:
            regularDict[field] = str(realDictRowObject[field])
        return regularDict

    def get_json_response(self, query):
        cursor = self.get_json_cursor()
        server_response = self.execute_and_fetch(cursor, query)
        response = []
        for row in server_response:
            response.append(self.__RealDictRowToRegularDict(row))
        return json.dumps(response)

    def add_user_login(self, data=None):
        cursor = self.get_json_cursor()
        #This is needed incase the table does not exist to prevent an error
        # cursor.execute(""" CREATE TABLE IF NOT EXISTS user_logins(  
        #                         user_id varchar(128),
        #                         device_type varchar(32),
        #                         masked_ip varchar(256),
        #                         masked_device_id varchar(256),
        #                         locale varchar(32), 
        #                         app_version integer,
        #                         create_date date
        #                         ); """)

        cursor.execute ("INSERT INTO user_logins(user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)" +
                        "VALUES ('" + str(data["user_id"]) + "', '" + str(data["device_type"]) + "', '" + str(data["masked_ip"]) + 
                        "', '" + str(data["masked_device_id"]) + "', '" + str(data["locale"]) + "', " + str(data["app_version"]).replace(".", "") + 
                        ", TO_DATE('" + str(datetime.today().strftime('%Y%m%d')) + "','YYYYMMDD'));")

    def __prettyPrintTable(self, table):
        header = self.db_fields
        rows =  [x.values() for x in table]
        print(tabulate.tabulate(rows, header))
            
    def get_user_logins(self, limit=None):
        query = "SELECT * FROM user_logins;" if limit == None else ("SELECT * FROM user_logins LIMIT " + str(limit) + ";")
        # print("Query chosen: ", query)
        self.__prettyPrintTable(json.loads(self.get_json_response(query)))