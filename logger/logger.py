from datetime import datetime
from pymongo import MongoClient
import os

def connectMongodb(mongohost, mongoPort, mongoDbName=None):
    client = MongoClient(mongohost,mongoPort)
    return client


def connectMongodbwithstring(mongoString):
    client = MongoClient(mongoString)
    print("Connect established")
    return client


class Log:
    def __init__(self):
        self.mongohost = os.getenv('mongoHost') if os.getenv('mongoHost') is not None else "localhost"
        self.mongoPort = os.getenv('mongoPort') if os.getenv('mongoPort') else 27017

        self.mongoString = os.getenv('CUSTOMCONNSTR_mongoString') if os.getenv('CUSTOMCONNSTR_mongoString') else "mongodb://localhost:27017"
        #self.mongoString = "mongodb://luis-db-testing:8JaplkTj6PjDx6OU6W3RIXXuynWfGq5SozSqNBamfoMHfPSwwsLltQe4zt4SWYA6n7W4pHFNmuO1Rj3gayxyIQ==@luis-db-testing.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@luis-db-testing@"
        self.mongoDbName = "luis_conv_logs"
        self.mongoClient = connectMongodbwithstring(self.mongoString)


    def write_log(self, sessionID, log_message):
        self.file_object = open("logs/"+sessionID+".txt", 'a+')
        self.now = datetime.now()
        self.date = self.now.date()
        self.current_time = self.now.strftime("%H:%M:%S")
        self.file_object.write(
            str(self.date) + "/" + str(self.current_time) + "\t\t" + log_message + "\n")
        self.file_object.close()

    def write_log_to_db(self, sessionID, log_message):
        self.now = datetime.now()
        self.date = self.now.date()
        self.current_time = self.now.strftime("%H:%M:%S")
        dataBase =  self.mongoClient['azureLuis']
        dictValues={}
        dictValues['timeStamp'] = str(self.date) + "/" + str(self.current_time)
        dictValues['message'] = log_message

        dataBase[sessionID].insert(dictValues)
        print(log_message," inserted successfully")