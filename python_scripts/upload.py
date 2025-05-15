import requests
import base64
import json
import os
from dotenv import load_dotenv

def upload_image_to_imgur(base64_image, image_title=None):
    """
    Upload a base64 encoded image to Imgur
    
    Args:
        base64_image (str): Base64 encoded image string (without the data:image/png;base64, prefix)
        image_title (str, optional): Title for the image
        
    Returns:
        dict: JSON response from Imgur API with image details
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Get client ID from environment variables
    client_id = os.getenv('IMGUR_CLIENT_ID')
    if not client_id:
        raise ValueError("IMGUR_CLIENT_ID not found in environment variables")
    
    # Imgur API endpoint for uploading images
    url = 'https://api.imgur.com/3/image'
    
    # Prepare headers with client ID for authorization
    headers = {
        'Authorization': f'Client-ID {client_id}'
    }
    
    # Prepare payload for the request
    payload = {
        'image': base64_image,
        'type': 'base64',
    }
    
    # Add title if provided
    if image_title:
        payload['title'] = image_title
    
    # Make the POST request to Imgur API
    response = requests.post(url, headers=headers, data=payload)
    
    # Check if request was successful
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    # Example usage:
    # 1. Read an image file and convert to base64
    with open("image.jpg", "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    # 2. Upload to Imgur
    response = upload_image_to_imgur(encoded_image, "My Uploaded Image")
    
    # 3. Print the URL of the uploaded image
    if response and response['success']:
        print(f"Image uploaded successfully!")
        print(f"Image URL: {response['data']['link']}")
    else:
        print("Failed to upload image")