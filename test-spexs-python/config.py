"""
Configuration module for loading environment variables
"""
import os
from dotenv import load_dotenv

environment = os.getenv('ENVIRONMENT')
if not environment:
    environment = 'development'
load_dotenv(f'.env.{environment}')

class Config:

    def __init__(self):
        self.hubspot_key = os.getenv('HUBSPOT_KEY')
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.mongo_db_name = os.getenv('MONGO_DB_NAME', 'hubspot_data')
        
        if not self.hubspot_key:
            raise ValueError("HUBSPOT_KEY not found in environment variables")
    
    @property
    def hubspot_api_key(self):
        return self.hubspot_key
    
    @property
    def mongodb_uri(self):
        return self.mongo_uri
    
    @property
    def mongodb_database(self):
        return self.mongo_db_name

config = Config()