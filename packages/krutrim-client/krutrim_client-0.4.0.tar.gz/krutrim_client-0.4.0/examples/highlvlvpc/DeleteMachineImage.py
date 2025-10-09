import os
from krutrim_client import KrutrimClient
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("API_KEY")

client = KrutrimClient(api_key=api_key)

try:
    delete_resp = client.highlvlvpc.delete_machine_image(
        image_krn="enter the image_krn",  
        
    )
    print(f"Image deleted successfully: {delete_resp}")
except Exception as e:
    print(f"Exception has occurred: {e}")
