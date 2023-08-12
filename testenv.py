from dotenv import load_dotenv
import os


load_dotenv()

api_key = os.getenv("API_KEY")
base_url = os.getenv('base_url')
bearer_token  = os.getenv('bearer_token')
consumer_key  = os.getenv('consumer_key')
consumer_secret = os.getenv('consumer_secret')
access_token = os.getenv('access_token')
access_token_secret  = os.getenv('access_token_secret')


print(access_token_secret)
