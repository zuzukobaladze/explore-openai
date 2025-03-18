"""
OpenAI Vision API Assignment

In this assignment, you will learn how to use OpenAI's Vision capabilities to analyze images.
You will implement functionality to extract information from images using multimodal models.

Learning objectives:
1. Understand multimodal inputs (text + images) with OpenAI API
2. Process image files for API consumption
3. Extract information from images using GPT-4 Vision
4. Handle detailed and low-resolution processing modes
5. Work with multiple images in a single request

Expected duration: 15-20 minutes
"""

import os
import base64
from dotenv import load_dotenv
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = OpenAI()


def encode_image(image_path):
    """
    Encode an image file to base64 string.

    Args:
        image_path (str): Path to the image file

    Returns:
        str: Base64 encoded string of the image
    """
    # TODO: Task 1 - Encode image to base64
    # 1. Open the image file in binary read mode
    # 2. Read the file content
    # 3. Encode the content to base64
    # 4. Return the base64 string in utf-8 format

    # Your code here

    return None  # Replace with your implementation


def analyze_image(image_path, prompt="What's in this image?", detail="auto"):
    """
    Analyze an image using OpenAI's Vision capabilities.

    Args:
        image_path (str): Path to the image file or URL
        prompt (str): The question or instruction about the image
        detail (str): Level of detail for analysis ("auto", "low", or "high")

    Returns:
        str: The AI's analysis of the image
    """
    # TODO: Task 2 - Prepare content for vision analysis
    # 1. Create a list with at least two items: text prompt and image
    # 2. For the text item, use type "text" and include the prompt
    # 3. For the image item, check if the path is a URL or local file:
    #    - If URL, use it directly in the image_url
    #    - If local file, encode it to base64 and format as a data URL
    # 4. Add the detail parameter to control analysis granularity

    # Your code here
    content = []

    # TODO: Task 3 - Call the OpenAI API for vision analysis
    # 1. Use client.chat.completions.create with the right model (gpt-4-vision-preview or equivalent)
    # 2. Pass the content list with text and image
    # 3. Set appropriate max_tokens (e.g., 500)
    # 4. Return the text content from the response

    # Your code here

    return "Image analysis would appear here"  # Replace with your implementation


def compare_images(image_paths, comparison_prompt="What are the differences between these images?"):
    """
    Compare multiple images using OpenAI's Vision capabilities.

    Args:
        image_paths (list): List of paths to image files or URLs
        comparison_prompt (str): The question about the differences or similarities

    Returns:
        str: The AI's comparison of the images
    """
    # TODO: Task 4 - Create a multi-image comparison request
    # 1. Create a content list starting with the text prompt
    # 2. Add each image to the content list (handling both URLs and local files)
    # 3. Call the API with the content list
    # 4. Return the analysis text

    # Your code here

    return "Image comparison would appear here"  # Replace with your implementation


def save_image_from_url(image_url, save_path):
    """
    Download an image from a URL and save it locally.

    Args:
        image_url (str): URL of the image
        save_path (str): Path where the image should be saved

    Returns:
        str: Path to the saved image
    """
    # TODO: Task 5 - Download and save an image from a URL
    # 1. Make a GET request to download the image
    # 2. Ensure the directory exists
    # 3. Save the image to the specified path
    # 4. Return the save path

    # Your code here

    return save_path  # Return the path where the image was saved


def main():
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    # Sample images - you can change these URLs or use local files
    sample_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"

    # TODO: Task 6 - Implement the main function
    # 1. Download a sample image from URL or use a local image
    # 2. Analyze the image with a custom prompt
    # 3. Try analyzing with both "high" and "low" detail settings and compare results
    # 4. If you have multiple images, try the compare_images function
    # 5. Print the analysis results

    # Your code here

    print("OpenAI Vision API Demo")
    print("-" * 30)

    # Download image

    # Analyze image

    # Compare detail levels

    # Optional: Compare multiple images


if __name__ == "__main__":
    main()