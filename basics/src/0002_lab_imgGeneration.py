import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import datetime

load_dotenv()
client = OpenAI()


def generate_image(prompt, style="vivid", size="1024x1024", quality="standard"):
    # TODO: Task 1 - Call the OpenAI API to generate an image
    # 1. Use client.images.generate with the appropriate parameters
    # 2. Use the dall-e-3 model
    # 3. Pass in the prompt, style, size, quality, and set n=1 (for 1 image)
    # 4. Return the API response

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        style=style,
        size=size,
        quality=quality,
        n=1
    )

    url = response.data[0].url
    print(url)
    return url  # Replace with your implementation


def save_image(image_url, filename):

    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    base_output_dir = "output"
    os.makedirs(base_output_dir, exist_ok=True)

    if not filename:
        filename = f"{timestamp}_generated.png"

    full_file_path = os.path.join(base_output_dir, filename)

    response = requests.get(image_url)

    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image.save(full_file_path)
        return full_file_path
    else:
        raise Exception(f"Failed to download image. Status code: {response.status_code}")


def compare_styles(prompt, output_dir="output"):
    # TODO: Task 3 - Generate and compare two different styles
    # 1. Generate an image with "vivid" style using the generate_image function
    # 2. Save the vivid image using the save_image function
    # 3. Generate an image with "natural" style
    # 4. Save the natural image
    # 5. Print the revised prompts for comparison
    # 6. Return the paths to both saved images

    image1_prompt = "A Bloodborne character emoting on defeated boss"
    image1_url = generate_image(image1_prompt)
    image1_path = save_image(image1_url, "bb_image")

    image2_prompt = "An Elden Ring character emoting on defeated boss"
    image2_url = generate_image(image2_prompt)
    image2_path = save_image(image2_url, "er_image")

    return image1_path, image2_path


def display_images(image_paths, titles=None, output_path="output/comparison.png"):
    if titles is None:
        titles = [f"Image {i + 1}" for i in range(len(image_paths))]

    # TODO: Task 4 - Display the images side by side
    # 1. Create a figure with subplots based on the number of images
    # 2. Load each image using PIL
    # 3. Display each image in a subplot with its title
    # 4. Save the comparison image instead of showing it (to avoid PyCharm backend issues)
    # 5. Try to open the saved image file using PIL

    n_images = len(image_paths)
    fig, axes = plt.subplots(1, n_images, figsize=(8 * n_images, 8))

    try:
        for i, (path, title) in enumerate(zip(image_paths, titles)):
            img = Image.open(path)
            axes[i].imshow(img)
            axes[i].set_title(title)
            axes[i].axis('off')  # Hide axes

        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        comparison_img = Image.open(output_path)
        comparison_img.show()

        return output_path

    except Exception as e:
        print(f"Error displaying images: {str(e)}")
        plt.close()
        return None


def main():
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    # TODO: Task 5 - Write a main program to demonstrate image generation
    # 1. Create a prompt for image generation
    # 2. Generate and save an image using default parameters
    # 3. Compare vivid and natural styles with the same prompt
    # 4. Display all generated images
    # 5. Print a summary of what was learned about the API's capabilities

    


if __name__ == "__main__":
    main()