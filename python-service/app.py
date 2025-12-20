from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
import os

MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client["tech-radar"]

articles_collection = db["articles"]

summary_collection = db["summaries"]

