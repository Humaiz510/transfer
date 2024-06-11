import requests
import boto3
from botocore.exceptions import NoCredentialsError

def upload_file_from_url_to_s3(url, bucket_name, s3_key):
    s3 = boto3.client('s3')

    try:
        # Stream the file content from the URL
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check if the request was successful
        
        # Upload the streamed content to S3
        s3.upload_fileobj(response.raw, bucket_name, s3_key)
        print(f"File uploaded to {bucket_name}/{s3_key} successfully.")
    
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file from URL: {e}")
    except NoCredentialsError:
        print("Credentials not available")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
file_url = 'https://example.com/path/to/your/file'
s3_bucket = 'your-s3-bucket'
s3_key = 'path/in/s3/to/store/file'

upload_file_from_url_to_s3(file_url, s3_bucket, s3_key)