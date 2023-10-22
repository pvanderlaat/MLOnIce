from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import dotenv_values


class DB:
    def __init__(self):
        password = dotenv_values(".env")["PASSWORD"]
        uri = "mongodb+srv://pvanderlaat:" + password + "@cluster0.jnprd5n.mongodb.net/?retryWrites=true&w=majority"
        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Connected to db")
        except Exception as e:
            print("Error connecting to db")
            print(e)
            exit()
    
    def insert(self):
        # Access your MongoDB database (replace 'your-database-name' with your actual database name)
        db = client['your-database-name']

        # Access the collection where you want to insert data (replace 'your-collection-name' with your collection name)
        collection = db['your-collection-name']

        # Define the data you want to insert as a Python dictionary
        data_to_insert = {
            "name": "John Doe",
            "age": 30,
            "email": "johndoe@example.com"
        }

        # Insert the data into the collection
        insert_result = collection.insert_one(data_to_insert)

        # Print the inserted document's ObjectId
        print("Inserted document ID:", insert_result.inserted_id)


