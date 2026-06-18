import argparse
import requests
import urllib.parse
import os
from tenacity import retry, wait_random_exponential, stop_after_attempt
from PIL import Image

# Translate aspect ratios to exact pixel dimensions
ASPECT_RATIOS = {
    "16:9": {"width": 1344, "height": 768},   # Landscape
    "1:1": {"width": 1024, "height": 1024},   # Square
    "9:16": {"width": 768, "height": 1344}    # Vertical
}

# API URL for image generation (No API key required)
BASE_API_URL = "https://image.pollinations.ai/prompt/"

# Setup command line arguments for terminal input
def get_user_input():
    parser = argparse.ArgumentParser(description="Enterprise Multimodal Image Studio")
    parser.add_argument("--prompt", type=str, required=True, help="Description of the image to generate")
    parser.add_argument("--ratio", type=str, choices=["16:9", "1:1", "9:16"], default="1:1", help="Aspect ratio of the image")
    parser.add_argument("--output", type=str, default="generated_artwork.png", help="Name of the output file")
    return parser.parse_args()

# Retry mechanism to handle network drops or server errors
@retry(wait=wait_random_exponential(min=2, max=10), stop=stop_after_attempt(3), reraise=True)
def generate_and_save_image(prompt, width, height, output_filename):
    encoded_prompt = urllib.parse.quote(prompt)
    final_url = f"{BASE_API_URL}{encoded_prompt}?width={width}&height={height}&nologo=true"
    
    print(f"\nSending payload to GPU cluster... Generating {width}x{height} image.")
    
    # Memory-Safe Streaming
    # Use stream=True to download the file in chunks and prevent RAM overflow
    response = requests.get(final_url, timeout=(3.05, 60), stream=True)
    
    if response.status_code != 200:
        raise Exception(f"Server Error {response.status_code}")
        
    print("Streaming data to local storage...")
    
    # Save the image in 64KB chunks to the local storage
    with open(output_filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
                
    # Binary Integrity Verification
    print("Verifying binary integrity (Pixel check)...")
    try:
        # Check the image using the Pillow library
        with Image.open(output_filename) as img:
            img.load() # Force Pillow to read every pixel to ensure it is fully downloaded
        print("Integrity Check Passed: Image is 100% complete and healthy.")
        
    except OSError as e:
        # If the image is corrupted, delete it and raise an error to trigger a retry
        if os.path.exists(output_filename):
            os.remove(output_filename)
        raise Exception(f"Data stream corrupted during download. File deleted. Retrying... Error: {e}")

def main():
    args = get_user_input()
    dimensions = ASPECT_RATIOS[args.ratio]
    
    print("--- Enterprise Image Studio Initialized ---")
    try:
        generate_and_save_image(args.prompt, dimensions["width"], dimensions["height"], args.output)
        print(f"\nSuccess! Artwork safely saved as '{args.output}'")
    except Exception as e:
        print(f"\nFailed to generate image. Error: {e}")

if __name__ == "__main__":
    main()