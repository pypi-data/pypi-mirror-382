from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")

client = KrutrimClient(api_key=api_key)

try:

    create_in_bucket_response = client.highlvlvpc.upload_image_s3(

        disk_format="enter the format",  
        image="enter presigned url",
        x_region = "enter the region"
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )

    print(f"{create_in_bucket_response}")

except Exception as e:
    print(f"Exception: {e}")
