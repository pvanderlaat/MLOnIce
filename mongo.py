from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import dotenv_values


class DB:
    def __init__(self):
        password = dotenv_values(".env")["PASSWORD"]
        uri = "mongodb+srv://pvanderlaat:" + password + "@cluster0.jnprd5n.mongodb.net/?retryWrites=true&w=majority"
        # Create a new client and connect to the server
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Connected to db")
        except Exception as e:
            print("Error connecting to db")
            print(e)
            exit()
    
    def insert(self, collection_name, document):
        # Access your MongoDB database (replace 'your-database-name' with your actual database name)
        db = self.client["Hockey"]

        # Access the collection where you want to insert data (replace 'your-collection-name' with your collection name)
        collection = db[collection_name]

        # Insert the data into the collection
        collection.insert_one(document)

        # Print the inserted document's ObjectId
        # print("Inserted document ID:", insert_result.inserted_id)

    def find(self, collection_name, filter_query):
        # Access your MongoDB database (replace 'your-database-name' with your actual database name)
        db = self.client["Hockey"]

        # Access the collection from which you want to retrieve data (replace 'your-collection-name' with your collection name)
        collection = db[collection_name]

        # Find all documents that match the filter query
        result = collection.find(filter_query)

        # Return the cursor containing the results
        return result


