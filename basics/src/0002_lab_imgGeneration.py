import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt

load_dotenv()
client = OpenAI()


def generate_image(prompt, style="vivid", size="1024x1024", quality="standard"):
    # TODO: Task 1 - Call the OpenAI API to generate an image
    # 1. Use client.images.generate with the appropriate parameters
    # 2. Use the dall-e-3 model
    # 3. Pass in the prompt, style, size, quality, and set n=1 (for 1 image)
    # 4. Return the API response

    # Your code here

    return None  # Replace with your implementation


def save_image(image_url, filename):
    # TODO: Task 2 - Download and save the image
    # 1. Make a GET request to download the image from the URL
    # 2. Create necessary directories if they don't exist
    # 3. Save the image to the specified filename
    # 4. Return the filename

    # Your code here

    return filename


def compare_styles(prompt, output_dir="output"):
    # TODO: Task 3 - Generate and compare two different styles
    # 1. Generate an image with "vivid" style using the generate_image function
    # 2. Save the vivid image using the save_image function
    # 3. Generate an image with "natural" style
    # 4. Save the natural image
    # 5. Print the revised prompts for comparison
    # 6. Return the paths to both saved images

    # Your code here

    return None, None  # Replace with your implementation


def display_images(image_paths, titles=None, output_path="output/comparison.png"):
    if titles is None:
        titles = [f"Image {i + 1}" for i in range(len(image_paths))]

    # TODO: Task 4 - Display the images side by side
    # 1. Create a figure with subplots based on the number of images
    # 2. Load each image using PIL
    # 3. Display each image in a subplot with its title
    # 4. Save the comparison image instead of showing it (to avoid PyCharm backend issues)
    # 5. Try to open the saved image file using PIL

    # Your code here


def main():
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    # TODO: Task 5 - Write a main program to demonstrate image generation
    # 1. Create a prompt for image generation
    # 2. Generate and save an image using default parameters
    # 3. Compare vivid and natural styles with the same prompt
    # 4. Display all generated images
    # 5. Print a summary of what was learned about the API's capabilities

    # Your code here


if __name__ == "__main__":
    main()